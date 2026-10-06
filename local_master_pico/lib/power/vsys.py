from machine import ADC, Pin

GP26 = 26            # input, pin 31,
Pin(GP26, Pin.IN)    # this was Pin.OUT and it still worked?
adc = ADC(GP26)      # GPIO26 -> ADC0
VREF = 3.3           # ADC reference voltage approx 3.3V
RT = 22000.0         # top resistor (ohms)
RB = 33000.0         # bottom resistor (ohms)
DIV_RATIO = (RT + RB) / RB  # 100000/60000 = 1.6666667

class VSYS:
    def read_vsys(self):
        raw = adc.read_u16()            # 0..65535
        vin_div = raw / 65535.0 * VREF
        vsys = vin_div * DIV_RATIO
        return vsys
