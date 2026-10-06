from machine import Pin, time_pulse_us
import time
#for pico_switch board
GP2  = 3    # is on PIN 4   output, HC_SR04P Trigger Output
GP3  = 2    # is on PIN 5   input,  HC_SR04P Echo Input

# for breadboard
#GP2  = 2    # is on PIN 4   output, HC_SR04P Trigger Output
#GP3  = 3    # is on PIN 5   input,  HC_SR04P Echo Input


#hc       = hcsr04(GP2, GP3) # trigger out, echo in
class HCSR04:
    def __init__(self):
        self.trig = Pin(GP2, Pin.OUT)
        self.echo = Pin(GP3, Pin.IN) # this was Pin.OUT and it still worked?
        pass

    def GetDistance(self):
        self.trig.value(0)
        time.sleep(0.05)
        self.trig.value(1)
        time.sleep(0.00001)  # 10 µs pulse
        self.trig.value(0)

        duration = time_pulse_us(self.echo, 1, 30000)  # timeout 30 ms
        if duration < 0:
            return None  # no echo received
        distance_cm = (duration / 2) / 29.1
        distance_inches  = distance_cm / 2.54
        return distance_inches