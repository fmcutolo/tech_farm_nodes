import time
from debug.uart import UART_FOR_DEBUG
debug = UART_FOR_DEBUG()


def DebugWrite(buf):
    debug.write_to(buf)
    
def DebugAny():
    return debug.received_any()

def DebugGetByte():
    return debug.get_byte()