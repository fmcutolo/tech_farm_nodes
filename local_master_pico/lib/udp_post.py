from time import sleep, ticks_ms, ticks_diff
import network
from credentials import WIFI_SSID, WIFI_PASSWORD
import gc
import socket
import json

SERVER_IP = "192.168.12.103"
SERVER_PORT = 55000

wlan = network.WLAN(network.STA_IF)
start = None
packet_number = 0
the_socket = None
def initialize_start_time():
    global start
    start = ticks_ms()

def connect_to_wifi():
    print("in connect_to_wifi()")
    wlan.active(True)
    wlan.config(pm=0xa11140)   # Disable Wi-Fi power management
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    while not wlan.isconnected():
        print(f"Attempting to connect to: {SERVER_IP}:{SERVER_PORT}, ssid = {WIFI_SSID}")
        sleep(1)

    print("WiFi connected:", wlan.ifconfig())



def close_socket(a_socket):
    try:
        if a_socket is None:
            print("Socket is None")
        else:
            a_socket.close()
            print("Existing socket closed")
    except OSError as e:
        print("Socket close failed:", e)
    
    return None

def create_socket():
    gc.collect()
    print("Free memory before socket creation:", gc.mem_free())

    a_socket = None
    try:
        print("Creating UDP socket")
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Socket created successfully")

        a_socket.settimeout(2)
        print("Timeout configured successfully")

    except (OSError, MemoryError) as e:
        print("Socket initialization failed:", e)
        print("Free memory:", gc.mem_free())
        close_socket(a_socket)
        return None
    return a_socket

def create_command_socket():
    global command_socket, command_address

    close_command_socket()
    command_address = None

    command_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    command_socket.bind(("0.0.0.0", COMMAND_PORT))
    command_socket.setblocking(False)
    return command_socket

def initialize_udp_post():
    global the_socket, command_socket
    initialize_start_time()
    connect_to_wifi()
    the_socket = create_socket()
    command_socket = create_command_socket()

def close_udp_post():
    close_socket(the_socket)

def flow(a_payload):
    global packet_number, the_socket
    while True:
        if the_socket is None:
            the_socket = create_socket()
            if the_socket is None:
                print("Socket creation failed, retrying...")
                sleep(3)
                continue
        try:
            stage = "sendto"
            #packet_number = a_payload["packet_number"]
            a_payload["packet_number"] = packet_number
            message = f"{packet_number}:Hello from Pico"
            data = json.dumps(a_payload).encode()
            send_to_results = the_socket.sendto(data, (SERVER_IP, SERVER_PORT))
            duration = ticks_diff(ticks_ms(), start)
            duration_float = f"{duration / 1000:.3f}"
            print(duration_float, "  sent: ", message,  "  send_to_result: ",send_to_results)
            
            stage = "recvfrom"
            data, address = the_socket.recvfrom(1024)
            print("Received:", data, "from:", address)
            received_ack = data.decode()  # ack is now a string
            expected_ack  = f"ack {packet_number}"
            
            if received_ack != expected_ack:
                raise ValueError(f"ACK mismatch: expected {expected_ack}, received {received_ack}")
            packet_number += 1

            return 1  # success, only return if post succeeded

        except (OSError, ValueError) as e:
            print("stage:",stage,"  UDP error:", e)
            if not wlan.isconnected():
                close_socket(the_socket) #returns None
                connect_to_wifi()
                the_socket = create_socket()
                if the_socket is None:
                    print("Unable to create UDP socket")
                else:
                    print("UDP socket ready")

            else:                
                sleep(3)


# **************** RECEIVE COMMANDS FROM SERVER
import errno

COMMAND_PORT = 55001
command_address = None
command_socket = None
print("just executed above")

def check_commands():
    global command_address

    try:
        data, command_address = command_socket.recvfrom(1024)
        return data.decode()

    except OSError as e:
        if e.errno != errno.EAGAIN:
            print("UDP receive error:", e)
        return None

def send_command_ack(a_message):
    if command_address is not None:
        command_socket.sendto(
            a_message.encode(),
            command_address
        )

def close_command_socket():
    close_socket(command_socket)