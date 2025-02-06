from machine import Pin, I2C
import time
from oled_72x40 import *

# Init Display
i2c  = I2C(0, scl=Pin(6), sda=Pin(5), freq=400000)
s = oled_72x40(i2c, rotation=1)
s.fill(0)

