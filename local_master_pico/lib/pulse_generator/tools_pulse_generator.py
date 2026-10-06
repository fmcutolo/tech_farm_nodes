from pulse_generator.pulse_generator import PulseGenerator, ISRTest, GenerateNoInterruptsPulse, kill_isr

pulser = PulseGenerator()

def generate_pulses(period_ms, width_ms,number_of_pulses = 0):
    pulser.start_pulses(period_ms, width_ms, number_of_pulses)

def kill_generate_pulses():
    pulser.stop()

def one_khz_interrupt(a_call_back_function):
    ISRTest(a_call_back_function)    

def kill_one_khz_interrupt():
    kill_isr()

DEFAULT_PERIOD_IN_MS = 1000
DEFAULT_WIDTH_IN_MS = 500
def GenerateAsyncPulses(period_in_ms = DEFAULT_PERIOD_IN_MS, width_in_ms = DEFAULT_WIDTH_IN_MS):
    GenerateNoInterruptsPulse(period_in_ms, width_in_ms)    
