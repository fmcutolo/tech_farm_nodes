#from bus.i2c_bus import i2c
#from machine import I2C
import time

AT24C32_I2C_ADDR = 0x57
class AT24C32:
    def __init__(self, i2c, addr = AT24C32_I2C_ADDR):
        self.i2c = i2c
        self.addr = addr

    def write(self, mem_addr, data: bytes):
        """Write bytes to EEPROM (handles page boundaries)."""
        PAGE_SIZE = 32

        idx = 0
        while idx < len(data):
            page_space = PAGE_SIZE - ((mem_addr + idx) % PAGE_SIZE)
            chunk = data[idx: idx + page_space]

            # 2-byte memory address prefix
            addr_bytes = bytes([(mem_addr + idx) >> 8, (mem_addr + idx) & 0xFF])
            self.i2c.writeto(self.addr, addr_bytes + chunk)

            idx += len(chunk)
            time.sleep_ms(5)  # EEPROM internal write delay

    def read(self, mem_addr, length):
        """Read bytes from EEPROM."""
        addr_bytes = bytes([mem_addr >> 8, mem_addr & 0xFF])
        self.i2c.writeto(self.addr, addr_bytes, False)
        return self.i2c.readfrom(self.addr, length)
