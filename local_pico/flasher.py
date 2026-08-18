from timersmanager import TimersManager
from machine import Pin

GP25 = 25
ON_BOARD_LED = GP25
led = Pin(ON_BOARD_LED, Pin.OUT)

class LEDFlasher:
    SHORT_PULSE_HI =    200 #tunable
    SHORT_PULSE_LO =    200 #tunable
    LONG_PULSE_LO  =  3_000 #tunable
    DEFAULT_NUMBER_OF_PULSES = 1

    IDLE_STATE = 0
    TURN_ON_STATE = 1
    COUNT_DOWN_ON_STATE = 2
    TURN_OFF_STATE =3
    LONG_DOWN_STATE =4
    
    def __init__(self):
        self.reload_number_of_pulses = self.DEFAULT_NUMBER_OF_PULSES
        self.number_of_pulses = 0    
        self.state = self.IDLE_STATE
        self.state_timer = TimersManager()
    
    def update_tick(self):  #call this in the main forever-loop   
        if (self.state == self.IDLE_STATE):
            pass
        
        elif (self.state == self.TURN_ON_STATE):
            led.on()
            self.state_timer.Start(0, self.SHORT_PULSE_HI)
            self.state = self.COUNT_DOWN_ON_STATE
        
        elif (self.state == self.COUNT_DOWN_ON_STATE):
            if self.state_timer.Expired(0):
                led.off()
                self.state_timer.Start(0, self.SHORT_PULSE_LO)
                self.state = self.TURN_OFF_STATE

        elif  (self.state == self.TURN_OFF_STATE):
             if self.state_timer.Expired(0):
                self.number_of_pulses -= 1
                if (self.number_of_pulses == 0):
                    self.state = self.LONG_DOWN_STATE
                    self.state_timer.Start(0, self.LONG_PULSE_LO)
                else:                    
                    self.state = self.TURN_ON_STATE

        elif (self.state == self.LONG_DOWN_STATE):
            if self.state_timer.Expired(0):
                self.number_of_pulses = self.reload_number_of_pulses
                self.state = self.TURN_ON_STATE        

    def load(self,number_of_pulses = DEFAULT_NUMBER_OF_PULSES):
        self.number_of_pulses = self.reload_number_of_pulses = number_of_pulses
        self.state = self.TURN_ON_STATE  #start
