##clear
from machine import Pin, Timer
from  time import sleep
from timersmanager import TimersManager

GP7 = 7
pin_number = GP7
class PulseGenerator:

    def __init__(self):

        self.pin = Pin(pin_number, Pin.OUT)
        self.pin.value(0)


    def start_pulses(self, pulse_period_ms,
                    pulse_width_ms, number_of_pulses=0):
        print("you're in the Pulse Generator!")
        self.pin = Pin(pin_number, Pin.OUT)
        self.pin.value(0)

        self.pulse_period_ms = pulse_period_ms - 1
        self.pulse_width_ms = pulse_width_ms - 1
        self.number_of_pulses = number_of_pulses

        self.counter = 0
        self.pulse_counter = 0
        self.run = True
        
        self.continuous = False
        if (self.number_of_pulses == 0):
            self.continuous = True


        self.timer = Timer()

        self.timer.init(
            period=1,
            mode=Timer.PERIODIC,
            callback=self.timer_isr
        )


    def timer_isr(self,timer):
        if self.run == False:
            return  
        
        if (self.counter == self.pulse_width_ms):
            self.pin.value(0)
            self.counter += 1
        elif (self.counter == self.pulse_period_ms):
            if self.continuous == True:
                self.pin.value(1)
                self.counter =0
            else:
                if self.pulse_counter == self.number_of_pulses:
                    #self.run = False
                    self.stop()
                else:    
                    self.pulse_counter += 1
                    self.pin.value(1)
                    self.counter = 0
        else:
            self.counter += 1

    def SetNumberOfPulses(self, number_of_pulses):
        self.number_of_pulses = number_of_pulses
        if (self.number_of_pulses == 0):
            self.continuous = True
        else:
            self.continuous = False

    def start(self):
        self.pulse_counter = 0
        self.counter = self.pulse_period_ms
        self.run = True

    def stop(self):
        self.run = False
        self.timer.deinit()
        self.pin.value(0)
        
isr_timer = None
def ISRTest(a_call_back_function):
    global isr_timer
    output_pin = Pin(pin_number, Pin.OUT) 

    # Timer interrupt service routine
    def timer_isr(isr_timer):
        output_pin.toggle()
        a_call_back_function()
    # Create timer
    isr_timer = Timer()

    # Generate interrupt every 1 ms
    isr_timer.init(
        period=1,
        mode=Timer.PERIODIC,
        callback=timer_isr
    )

def kill_isr():
    isr_timer.deinit()


import time
PERIOD_DURATION_IN_MS = 1000
WIDTH_DURATION_IN_MS = 500
def GenerateNoInterruptsPulse(pulse_period_in_ms=PERIOD_DURATION_IN_MS, 
                              pulse_width_in_ms = WIDTH_DURATION_IN_MS):  
    pulse = Pin(pin_number, Pin.OUT)
    pico_timer = TimersManager()
    pico_timer.Start("pulse_period_timer",pulse_period_in_ms)
    pico_timer.Start("pulse_width_timer", pulse_width_in_ms)
    state = 1
    pulse.value(state)
    
    while True:

        if state:
            if pico_timer.Expired("pulse_width_timer"):
                state = 0
                pulse.value(state)

        else:
            if pico_timer.Expired("pulse_period_timer"):
                state = 1
                pulse.value(state)

                pico_timer.ReStart("pulse_period_timer")
                pico_timer.ReStart("pulse_width_timer")                
