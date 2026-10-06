from machine import UART, Pin
GP16 = 16
GP17 = 17
#uart     = UART(0, baudrate=115200, tx=Pin(GP16), rx=Pin(GP17), timeout=1000)
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
