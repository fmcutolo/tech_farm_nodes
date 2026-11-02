from time import sleep, ticks_ms, ticks_diff
#import network
#from credentials import WIFI_SSID, WIFI_PASSWORD
#import socket
from udp_post import flow, initialize_udp_post, close_udp_post
from machine import Pin
from water_storage import save_total_pulses, load_total_pulses
from timersmanager import TimersManager

# ****************************  MAIN LOOP  *********************************

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

def save_if_changed():
    global last_saved_pulses

    current_pulses = total_pulses

    if current_pulses != last_saved_pulses:
        save_total_pulses(current_pulses)
        last_saved_pulses = current_pulses

def post_if_changed(message):
    global last_posted_pulses, last_posted_flow_rate

    current_pulses = total_pulses
    if (current_pulses != last_posted_pulses or
        last_posted_flow_rate is None or
        abs(flow_rate - last_posted_flow_rate) > FLOW_RATE_TOLERANCE):

        current_gallons = convert_to_gallons(current_pulses)

        print("POST starting:", message, ticks_ms())
        payload["total_gallons"] = current_gallons
        payload["total_pulses"]  = total_pulses
        payload["flow_rate"] = flow_rate
        flow(payload)
        print("POST finished:", message, ticks_ms())   
        print()

        last_posted_pulses = current_pulses
        last_posted_flow_rate = flow_rate



total_pulses = load_total_pulses()
PULSES_PER_GALLON = 450 * 3.78541   # (450 pulses/Liter) (3.78541 Liters/Gallon) 
print("Initializing total_pulses: ",total_pulses)
total_gallons = total_pulses / PULSES_PER_GALLON
last_saved_pulses = total_pulses
last_posted_pulses = None
last_posted_flow_rate = None

PULSES_PER_GALLON = 450 * 3.78541   # (450 pulses/Liter) (3.78541 Liters/Gallon) 

initialize_udp_post()


print("version 6")
METER_ID = "meter_1"
SESSION_ID = "ss1"
debug_string = "initially no errors"
packet_number = 0
payload = {
    "meter_id": METER_ID,
    "session_id": SESSION_ID,
    "total_gallons": packet_number,
    "flow_rate": 1,
    "total_pulses":2, #  for debug only
    "debug_string":debug_string
}

initialize_edge_isr()
post_update_timer = TimersManager()
post_update_timer.Start("post_it",3000) 
post_update_timer.Start("flow_rate",60000)  
post_update_timer.Start("tester",15000)  
testit = True

last_gallon_count = total_gallons
last_flow_time = ticks_ms()
flow_rate = 0.0
last_flow_rate = 0.0
FLOW_RATE_TOLERANCE = 0.01

try:
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
            flow_rate = gallons_measured * 60000 / elapsed_ms
            print("60sec: Elapsed ms=", elapsed_ms, "  Gallons=", gallons_measured, "  GPM=", flow_rate)
            last_gallon_count = total_gallons
            last_flow_time = now
            post_if_changed("60secPost:")

        if post_update_timer.Expired("post_it"):
            post_update_timer.ReStart("post_it")
            save_if_changed()
            post_if_changed("3secPost:")

        if post_update_timer.Expired("tester"):
            post_update_timer.ReStart("tester")
            total_pulses += 1703/4



except KeyboardInterrupt:
    print("\nCtrl+C received - stopping program")

finally:
    print("Cleaning up resources")
    close_udp_post() 
    print("Program terminated")

