# documentation:
# https://docs.micropython.org/en/latest/library/machine.UART.html
"""
class CommDevice:
    def __init__(self) -> None:
        self.uart = UART(0, baudrate=115200, tx=Pin(GP16), rx=Pin(GP17), timeout=1000)

    def write_to(self,byte_array_message):
        self.uart.write(byte_array_message)
    
    def received_any(self):
        return self.uart.any()

    def get_byte(self):
        return self.uart.read(1)

    def get_line(self):
        return self.uart.readline()

keyword arguments:
    baudrate - is the clock rate.
    tx - specifies the TX pin to use.

    rx - specifies the RX pin to use.

    timeout -  specifies the time to wait for the first character (in ms).
"""

from machine import UART, Pin
#uart      = UART(1, baudrate=115200, tx=Pin(GP8),  rx=Pin(GP9), timeout=1000)
GP8=8
GP9=9

class UART_FOR_DEBUG:
    def __init__(self) -> None:
#        self.uart = UART(1, baudrate=115200, tx=Pin(GP8), rx=Pin(GP9), timeout=1000)
        self.uart = UART(1, baudrate=115200, tx=Pin(GP8), rx=Pin(GP9), timeout=1000)
    def write_to(self,byte_array_message):
        self.uart.write(byte_array_message)
    
    def received_any(self):
        return self.uart.any() 

    def get_byte(self):
        return self.uart.read(1) # returns a byte array of length 1

    def get_line(self):
        return self.uart.readline()
