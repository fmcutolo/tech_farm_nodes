import network
from time import sleep, time, ticks_ms, ticks_diff
import requests
from pulse_generator.tools_pulse_generator import generate_pulses,one_khz_interrupt, GenerateAsyncPulses, kill_generate_pulses, kill_one_khz_interrupt
from timersmanager import TimersManager
from machine import Pin
from credentials import WIFI_SSID, WIFI_PASSWORD
import socket
import json

SERVER = "http://192.168.12.103:5000"
total_gallons = 0

def connect_to_wifi():
    # ssid = WIFI_SSID
    # password = WIFI_PASSWORD
    print("in connect_to_wifi()")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm=0xa11140)   # Disable Wi-Fi power management
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    while not wlan.isconnected():
        print("Attempting to connect to: ", SERVER, "  ssid = ", WIFI_SSID)
        sleep(0.5)

    print("WiFi connected:", wlan.ifconfig())

def post_flow(total_gallons, flow_rate):
    host = "192.168.12.103"
    port = 5000

    body = json.dumps({
        "total_gallons": total_gallons,
        "flow_rate": flow_rate
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

def log_post_to_csv(total_gallons, duration, rssi, result):
    with open("wifi_log.csv", "a") as f:
        f.write("{},{},{},{}\n".format(
            total_gallons,
            duration,
            rssi,
            result
        ))

# Interrupt Service Routine
def edge_isr(pin):
    global total_gallons
    total_gallons += 1

def initialize_edge_isr():
# Interrupt on rising edge
    input_pin = Pin(12, Pin.IN, Pin.PULL_DOWN)
    input_pin.irq(trigger=Pin.IRQ_RISING, handler=edge_isr)


initialize_edge_isr()
connect_to_wifi()

# NB Pulses and Gallons are used interchangeably, an 1 pulse = 1 gallon

# 1000, 1/1000 = 1 pulses/sec, in one minute (60 pulses/min)  = 60 gallons/minute
PERIOD_IN_MS = 1000
WIDTH_IN_MS  = 100
NUMBER_OF_PULSES = 0 # 0 = continuous
generate_pulses(PERIOD_IN_MS,WIDTH_IN_MS, NUMBER_OF_PULSES)

post_update_timer = TimersManager()
post_update_timer.Start("post_it",10000) 
post_update_timer.Start("flow_rate",60000)  

last_pulse_count = total_gallons
last_flow_time = ticks_ms()
flow_rate = 0.0

while True:

    # -----------------------------------
    # Calculate flow rate every 60 seconds
    # -----------------------------------
    if post_update_timer.Expired("flow_rate"):

        now = ticks_ms()
        #current_count = total_gallons

        elapsed_ms = ticks_diff(now, last_flow_time)
        pulse_difference = total_gallons - last_pulse_count

        if elapsed_ms > 0:
            flow_rate = pulse_difference * 60000 / elapsed_ms

        print("Elapsed milliseconds:", elapsed_ms)
        print("Pulses counted:", pulse_difference)
        print("Calculated GPM:", flow_rate)

        last_pulse_count = total_gallons
        last_flow_time = now

        post_update_timer.ReStart("flow_rate")

    # -----------------------------------
    # Send readings to Flask Server
    # -----------------------------------
    if post_update_timer.Expired("post_it"):
        post_update_timer.ReStart("post_it")
        print("Posting total_gallons =", total_gallons)
        print("Posting flow_rate =", flow_rate)

        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            print("Wi-Fi Disconnected!")

        post_flow(total_gallons, flow_rate)
    sleep(1)


# ******************  generate_pulses() usage
# uses timer interrupts
#example 1
# PERIOD_IN_MS = 4
# WIDTH_IN_MS = 1
# NUMBER_OF_PULSES = 3 # 0 = continuous
# generate_pulses(PERIOD_IN_MS,WIDTH_IN_MS, NUMBER_OF_PULSES)
# some_counter = 0
# while 1:
#     sleep(1)
#     print("generate_pulses(): some_counters=",some_counter)
#     some_counter += 2

#example 2
# PERIOD_IN_MS = 2
# WIDTH_IN_MS = 1
# NUMBER_OF_PULSES = 0 
# generate_pulses(PERIOD_IN_MS,WIDTH_IN_MS, NUMBER_OF_PULSES)
# some_counter = 0
# while 1:
#     sleep(1)
#     print("generate_pulses(): some_counters=",some_counter)
#     some_counter += 2

# ******************  one_khz_interrupt() usage
millisecond_counter = 0
def this_function_is_a_callback():
    global millisecond_counter
    millisecond_counter += 1
    
some_counter = 0
one_khz_interrupt(this_function_is_a_callback)
while 1:
    sleep(1)
    print("some_counters=",some_counter, "    milliseconds counter = ", millisecond_counter)
    some_counter += 1

# ******************  GenerateAsyncPulses()
# Interrupts are not used
PERIOD_IN_MS = 100
WIDTH_IN_MS = 50
GenerateAsyncPulses(PERIOD_IN_MS, WIDTH_IN_MS) # Note it does not return!

# 
# the following defaults to period = 1000 msecs, and width = 500 msec
GenerateAsyncPulses() # Note it does not return!

