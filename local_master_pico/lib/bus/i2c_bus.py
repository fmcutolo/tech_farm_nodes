from machine import Pin, I2C

# Create the shared I2C instance once
i2c = I2C(1, sda=Pin(10), scl=Pin(11)) #GP10 (physical pin 14), GP11 (physical pin 15)