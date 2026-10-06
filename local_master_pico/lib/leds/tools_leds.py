from leds.leds import LEDS, LED_ON, LED_OFF

leds = LEDS()
current_state = LED_OFF 

def LedTurnOn():
        global current_state
        current_state = LED_ON
        leds.Control(current_state)

def LedTurnOff():
        global current_state
        current_state = LED_OFF
        leds.Control(current_state)

def LedToggle():
    global current_state
    if current_state == LED_ON:
        current_state = LED_OFF
    else:
        current_state = LED_ON
    leds.Control(current_state)
