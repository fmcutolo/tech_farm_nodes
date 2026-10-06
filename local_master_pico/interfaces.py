from machine import Pin, time_pulse_us
import time

class hcsr04:
    def __init__(self, trig_output_pin, echo_input_pin):
        self.trig = Pin(trig_output_pin, Pin.OUT)
        self.echo = Pin(echo_input_pin, Pin.OUT)
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

# ***************************************************************
class RGB_Leds:
    # RGB_COLORS = {  'red':     (1, 1, 0),
    #                 'green':   (1, 0, 1),
    #                 'blue':    (0, 1, 1),
    #                 'yellow':  (1, 0, 0),
    #                 'magenta': (0, 1, 0),
    #                 'cyan':    (0, 0, 1),
    #                 'white':   (0, 0, 0),
    #                 'off':     (1, 1, 1),
    #                 }
    RGB_COLORS = {  'red':     (0, 1, 1),
                    'green':   (1, 0, 1),
                    'blue':    (1, 1, 0),
                    'yellow':  (0, 0, 1),
                    'magenta': (0, 1, 0),
                    'cyan':    (1, 0, 0),
                    'white':   (0, 0, 0),
                    'off':     (1, 1, 1),
                    }
    
    def __init__(self, red_pin, green_pin, blue_pin):
        self.r_led      = Pin(red_pin,   Pin.OUT) #red
        self.g_led      = Pin(green_pin, Pin.OUT) #green
        self.b_led      = Pin(blue_pin,  Pin.OUT) #blue

    def Control(self, color):
        color_tuple = self.RGB_COLORS[color]
        self.r_led.value(color_tuple[0])
        self.g_led.value(color_tuple[1])
        self.b_led.value(color_tuple[2])

    def Test(self,delay_in_seconds = 1):
        test_order= ['red',
                    'green',
                    'blue',
                    'yellow',
                    'magenta',
                    'cyan',
                    'white',
                    'off'
                    ]
    #    for color in rgb_color.keys():  #in MicroPython the order of dict.keys() is not guaranteed
    #                                    #it is guaranteed in Python 3.7+
        for color in test_order:
            print(f"RGB LED TEST: {color}")
            self.Control(color)
            time.sleep(delay_in_seconds)
