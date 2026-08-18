from machine import Pin
GP4=4 # pin 6, RED,   output
GP5=5 # pin 7, GREEN, output
GP6=6 # pin 9, BLUE,  output
#common ANODE, 0 = On, 1 = Off

RGB_COLORS = {  'red':     (0, 1, 1),
                'green':   (1, 0, 1),
                'blue':    (1, 1, 0),
                'yellow':  (0, 0, 1),
                'magenta': (0, 1, 0),
                'cyan':    (1, 0, 0),
                'white':   (0, 0, 0),
                'off':     (1, 1, 1),
                }


class RGB_LEDS:

    def __init__(self):
        self.r_led      = Pin(GP4,  Pin.OUT) #red
        self.g_led      = Pin(GP5,  Pin.OUT) #green
        self.b_led      = Pin(GP6,  Pin.OUT) #blue

    
    def Control(self, color):
        if color not in RGB_COLORS:
            print(f"color {color} is not a defined color, allowed colors: {list(RGB_COLORS.keys())}")
        else:
            color_tuple = RGB_COLORS[color]
            self.r_led.value(color_tuple[0])
            self.g_led.value(color_tuple[1])
            self.b_led.value(color_tuple[2])

LED_ON  = 0
LED_OFF = 1
GP1=1 # LED

class GenericLed:
    def __init__(self):
        self.led      = Pin(GP1,  Pin.OUT)
        self.current_state = LED_OFF
        self.led.value(self.current_state)
    
    def TurnOn(self):
        self.current_state = LED_ON
        self.led.value(self.current_state)
        
    def TurnOff(self):
        self.current_state = LED_OFF
        self.led.value(self.current_state)

    def Toggle(self):
        if self.current_state == LED_ON:
            self.current_state = LED_OFF
        else:
            self.current_state = LED_ON
        self.led.value(self.current_state)
