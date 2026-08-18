from bus.i2c_bus import i2c

def list_i2c_devices():
    """
    Returns a list of detected I2C addresses.
    """
    return i2c.scan()
