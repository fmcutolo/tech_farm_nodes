from  bus.i2c_bus import i2c
from  rtc.ds3231  import DS3231, DS3231_I2C_ADDR
rtc = DS3231(i2c)

#note that i2c.scan returns a list of i2c devices on the bus
#def rtc_present():
#    return DS3231_I2C_ADDR in i2c.scan()
def rtc_present():
    devices = i2c.scan()
    print("devices:", [hex(d) for d in devices])
    return DS3231_I2C_ADDR in devices

def GetDateTime():
    year,  month, day, weekday, hour, minutes, seconds, place_holder = rtc.datetime()
    return year,  month, day, weekday, hour, minutes, seconds

def SetDateTime(datetime):
    rtc = DS3231(i2c)
    rtc.datetime(datetime)


def GetTemperatureOnBoard():
    TEMP_MSB_REG = 0x11     # Temperature MSB register
    TEMP_LSB_REG = 0x12     # Temperature LSB register

    # Read two bytes from the temperature registers
    temp_bytes = i2c.readfrom_mem(DS3231_I2C_ADDR, TEMP_MSB_REG, 2)

    msb = temp_bytes[0]
    lsb = temp_bytes[1]

    # Combine MSB and LSB
    # The LSB contains the fractional part in the upper 2 bits
    temperature = msb + (lsb >> 6) * 0.25
    return temperature

def ConvertCentigradeToFahrenheit(centigrade):
    fahrenheit = centigrade * 9 / 5 + 32
    return fahrenheit



