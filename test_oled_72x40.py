from machine import Pin, I2C
from time import sleep_ms
from oled_72x40 import *

# Init Display
i2c  = I2C(0, scl=Pin(6), sda=Pin(5), freq=400000)
s = oled_72x40(i2c, rotation=0)
s.fill(0)

#  lines
for c in range(1,-1, -1):
    for line in range(0, 40, 4):
        s.line_(0, 0, 72, line, c)
        s.show()
        sleep_ms(20)
    for col in range(71, -1, -4):
        s.line_(0, 0, col, 39, c)
        s.show()
        sleep_ms(20)

sleep_ms(1000)
s.clear()

# rectangles
for c in range(1, -1, -1):
    x, y = 0, 0
    for w, h in ((70, 38), (60, 34), (50, 29), (40, 24), (30, 19)):
        s.rect_(x, y, w, h, c)
        s.show()
        x += 2
        y += 2
        sleep_ms(200)

sleep_ms(1000)
s.clear()

# ellipses
for r in range(12, 6, -1):
    for xc, yc in ((17,13),(35,13),(53,13),(26,26),(44,26)):
        s.ellipse_(xc, yc, r, r, 1)
        s.show()
        sleep_ms(50)

sleep_ms(1000)
s.clear()

for c in range(1, -1, -1):
    for q in (0b0001, 0b0011, 0b0111, 0b1111):
        s.ellipse_(36, 20, 25, 15, c, 0, q)
        s.show()
        sleep_ms(200)
    s.ellipse_(36, 20, 25, 15, c)
    sleep_ms(1000)

for c in range(1, -1, -1):
    for q in (0b0001, 0b0011, 0b0111, 0b1111):
        s.ellipse_(36, 20, 25, 15, c, 1, q)
        s.show()
        sleep_ms(200)
    s.ellipse_(36, 20, 25, 15, c)
    sleep_ms(1000)

#  text
string = 'font8'
for c in range(1, -1, -1):
    for n in range(1, len(string)+1):
        s.text8(string[:n], 0, 16, c)
        s.show()
        sleep_ms(500)

for x in range(0, 72):
    s.text8(string, x, 16)
    s.show()
    sleep_ms(20)
    s.text8(string, x, 16, 0)

for y in range(0, 41):
    s.text8(string, 15, y)
    s.show()
    sleep_ms(20)
    s.text8(string, 15, y, 0)

string = 'font16'
for c in range(1, -1, -1):
    for n in range(1, len(string)+1):
        s.text16(string[:n], -3, 12, c)
        s.show()
        sleep_ms(500)

for x in range(-3, 72):
    s.text16(string, x, 12)
    s.show()
    s.text16(string, x, 12, 0)

for y in range(0, 41):
    s.text16(string, -3, y)
    s.show()
    s.text16(string, -3, y, 0)
    
sleep_ms(1000)
s.clear()
for _ in range(5):
    s.text16("End!", 10, 12)
    s.show()
    sleep_ms(300)
    s.text16("End!", 10, 12, 0)
    s.show()
    sleep_ms(300)

string = "Thank you for watching..."
for x in range(0, len(string)*12):
    s.text16(string[x//12:x//12+7], -x + (x//12)*12 , 12)
    s.show()
    s.text16(string[x//12:x//12+7], -x + (x//12)*12, 12, 0)
