from bus.i2c_bus import i2c
from eeprom.at24c32 import AT24C32, AT24C32_I2C_ADDR
eeprom = AT24C32(i2c)

#note that i2c.scan returns a list of i2c devices on the bus
def eeprom_present():
    return AT24C32_I2C_ADDR in i2c.scan()

def write_to_eeprom(address, data):
    eeprom.write(address, data)

def read_from_eeprom(address, number_of_bytes):
    result = eeprom.read(address, number_of_bytes)
    return result
    
def dump_eeprom(start=0, length=256):
    """
    Dump EEPROM in rows. Each row shows:
    address (hex), decimal, hex, ascii
    """

    data = eeprom.read(start, length)

    for offset, b in enumerate(data):
        addr = start + offset

        # hex address
        addr_hex = f"0x{addr:04X}"

        # decimal and hex
        dec_val = f"{b:3d}"
        hex_val = f"0x{b:02X}"

        # ASCII or dot
        ascii_val = chr(b) if 32 <= b <= 126 else '.'

        print(f"{addr_hex}   {dec_val}   {hex_val}   {ascii_val}")
        
def dump_eeprom_16(start=0, length=256):
    """
    Print EEPROM contents in 16-byte rows:
    0000: 48 65 6C 6C 6F ...  | Hello.....
    Works on MicroPython builds that lack str.ljust().
    """
    data = eeprom.read(start, length)

    ROW_BYTES = 16
    HEX_FIELD_WIDTH = ROW_BYTES * 3 - 1  # "HH HH ... HH" => 16*3-1 = 47

    for row in range(0, length, ROW_BYTES):
        chunk = data[row:row+ROW_BYTES]
        addr = start + row

        # Left: address
        line = f"{addr:04X}: "

        # Middle: hex bytes (space separated)
        hex_bytes = " ".join("{:02X}".format(b) for b in chunk)

        # Manual padding because str.ljust may be missing
        pad_len = HEX_FIELD_WIDTH - len(hex_bytes)
        if pad_len > 0:
            hex_bytes = hex_bytes + (" " * pad_len)

        # Right: ASCII
        ascii_bytes = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)

        print("{0}{1}  | {2}".format(line, hex_bytes, ascii_bytes))
        