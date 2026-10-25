import network
from time import sleep, time, ticks_ms, ticks_diff
from timersmanager import TimersManager
from machine import Pin
from credentials import WIFI_SSID, WIFI_PASSWORD
import socket
import json
from water_storage import save_total_pulses, load_total_pulses


def connect_to_wifi():
    # ssid = WIFI_SSID
    # password = WIFI_PASSWORD
    global wlan
    print("in connect_to_wifi()")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm=0xa11140)   # Disable Wi-Fi power management
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    while not wlan.isconnected():
        print("Attempting to connect to: ", SERVER, "  ssid = ", WIFI_SSID)
        sleep(0.5)

    print("WiFi connected:", wlan.ifconfig())

def post_flow(total_gallons, flow_rate, total_pulses):
    host = "192.168.12.103"
    port = 5000

    body = json.dumps({
        "meter_id": METER_ID,
        "session_id": SESSION_ID,
        "total_gallons": total_gallons,
        "flow_rate": flow_rate,
        "total_pulses":total_pulses #  for debug only
    }).encode()

    request = (
        "POST /flow HTTP/1.0\r\n"
        "Host: {}\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(host, len(body)).encode() + body

    sock = None
    start = ticks_ms()

    try:
        sock = socket.socket()
        sock.settimeout(3)
        sock.connect((host, port))

        # Send the complete HTTP request
        sock.sendall(request)

        # Receive the beginning of Flask's response
        #response = sock.recv(512)

        #get the whole response instead.
        response = b""
        while True:
            chunk = sock.recv(512)
            if not chunk:
                break
            response += chunk

        duration = ticks_diff(ticks_ms(), start)

        status_line = response.split(b"\r\n", 1)[0]

        print("HTTP response:", status_line,"   WiFi RSSI:", wlan.status("rssi"), "dBm" )
        print("POST duration:", duration, "ms")
        print()

        return duration

    except OSError as e:
        duration = ticks_diff(ticks_ms(), start)
        print("POST failed:", e)
        print("POST duration:", duration, "ms")
        return None

    finally:
        if sock is not None:
            sock.close()

def check_if_to_post():
    global last_saved_pulses
    current_pulses = total_pulses
    print("current_pulses=", current_pulses, "   last_saved_pulses=", last_saved_pulses)
    if (current_pulses != last_saved_pulses):
        print("b:")
        save_total_pulses(current_pulses)
        last_saved_pulses = current_pulses

        # Calculate current gallons
        total_gallons = convert_to_gallons(current_pulses)

        print("Posting total_gallons =", total_gallons)
        print("Posting flow_rate =", flow_rate)
        print("Posting total_pulses =", current_pulses)
        post_flow(total_gallons, flow_rate, current_pulses)

# Interrupt Service Routine
def edge_isr(pin):
    global total_pulses
    total_pulses += 1

def initialize_edge_isr():
# Interrupt on rising edge
    input_pin = Pin(12, Pin.IN, Pin.PULL_DOWN)
    input_pin.irq(trigger=Pin.IRQ_RISING, handler=edge_isr)

def convert_to_gallons(total_pulses):
    return total_pulses / PULSES_PER_GALLON



METER_ID = "irrigation_1"
SERVER = "http://192.168.12.103:5000"
SESSION_ID = 22
PULSES_PER_GALLON = 450 * 3.78541   # (450 pulses/Liter) (3.78541 Liters/Gallon) 
total_pulses = load_total_pulses()
print("Initializing total_pulses: ",total_pulses)
total_gallons = total_pulses / PULSES_PER_GALLON
last_saved_pulses = total_pulses

initialize_edge_isr()
connect_to_wifi()

post_update_timer = TimersManager()
post_update_timer.Start("post_it",2000) 
post_update_timer.Start("flow_rate",60000)  

last_gallon_count = total_gallons
last_flow_time = ticks_ms()
flow_rate = 0.0
last_flow_rate = 0.0
post_flow(total_gallons, flow_rate, total_pulses)
FLOW_RATE_TOLERANCE = 0.01
while True:

    # -----------------------------------
    # Calculate flow rate every 60 seconds
    # -----------------------------------
    if post_update_timer.Expired("flow_rate"):
        post_update_timer.ReStart("flow_rate")

        now = ticks_ms()
        total_gallons = convert_to_gallons(total_pulses)

        elapsed_ms = ticks_diff(now, last_flow_time)
        gallons_measured = total_gallons - last_gallon_count

        if elapsed_ms > 0:
            flow_rate = gallons_measured * 60000 / elapsed_ms

        print("60min: Elapsed milliseconds=", elapsed_ms)
        print("60min: Gallons measured=", gallons_measured)
        print("60min: Calculated GPM=", flow_rate)

        last_gallon_count = total_gallons
        last_flow_time = now
        if abs(flow_rate - last_flow_rate) > FLOW_RATE_TOLERANCE:
            last_flow_rate = flow_rate
            print("60min: Posting total_gallons =", total_gallons)
            print("60min: Posting flow_rate =", flow_rate)
            print("60min: Posting total_pulses =", total_pulses)
            post_flow(total_gallons, flow_rate, total_pulses)

           
        

    # -----------------------------------
    # Send readings to Flask Server
    # -----------------------------------
    if post_update_timer.Expired("post_it"):
        post_update_timer.ReStart("post_it")
        check_if_to_post()

    sleep(1)

