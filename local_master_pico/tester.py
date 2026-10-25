from water_storage import save_total_pulses, load_total_pulses

total_pulses = load_total_pulses()
print("initial total_pulses", total_pulses)



from pulse_generator.tools_pulse_generator import generate_pulses,one_khz_interrupt, GenerateAsyncPulses, kill_generate_pulses, kill_one_khz_interrupt
from time import sleep


# NB Pulses and Gallons are used interchangeably

# use generate_pulses() when simulating a flow meter
# but if you do use generate_pulses() make sure you call kill_generate_pulses() after Ctrl+c
# 
# KeyboardInterrupt:
# >>> kill_generate_pulses()
# >>>
# 
# 1000, 1/1000 = 1 pulses/sec, in one minute (60 pulses/min)  = 60 gallons/minute
# PERIOD_IN_MS = 1000
# WIDTH_IN_MS  = 100
# NUMBER_OF_PULSES = 0 # 0 = continuous
# generate_pulses(PERIOD_IN_MS,WIDTH_IN_MS, NUMBER_OF_PULSES)

# ******************  generate_pulses() usage
# uses timer interrupts
#example 1
# PERIOD_IN_MS = 4
# WIDTH_IN_MS = 1
# NUMBER_OF_PULSES = 3 # 0 = continuous
# generate_pulses(PERIOD_IN_MS,WIDTH_IN_MS, NUMBER_OF_PULSES)
# some_counter = 0
# while 1:
#     sleep(1)
#     print("generate_pulses(): some_counters=",some_counter)
#     some_counter += 2

#example 2
# PERIOD_IN_MS = 2
# WIDTH_IN_MS = 1
# NUMBER_OF_PULSES = 0 
# generate_pulses(PERIOD_IN_MS,WIDTH_IN_MS, NUMBER_OF_PULSES)
# some_counter = 0
# while 1:
#     sleep(1)
#     print("generate_pulses(): some_counters=",some_counter)
#     some_counter += 2

# ******************  one_khz_interrupt() usage
millisecond_counter = 0
def this_function_is_a_callback():
    global millisecond_counter
    millisecond_counter += 1
    
some_counter = 0
one_khz_interrupt(this_function_is_a_callback)
while 1:
    sleep(1)
    print("some_counters=",some_counter, "    milliseconds counter = ", millisecond_counter)
    some_counter += 1

# ******************  GenerateAsyncPulses()
# Interrupts are not used
PERIOD_IN_MS = 100
WIDTH_IN_MS = 50
GenerateAsyncPulses(PERIOD_IN_MS, WIDTH_IN_MS) # Note it does not return!

# 
# the following defaults to period = 1000 msecs, and width = 500 msec
GenerateAsyncPulses() # Note it does not return!

