from machine import Pin

LED_ON  = 0
LED_OFF = 1
GP1=1 # LED

class LEDS:
    def __init__(self):
        self.led      = Pin(GP1,  Pin.OUT)
        self.led.value(LED_OFF)
    
    def Control(self,led_state):
        self.led.value(led_state)



