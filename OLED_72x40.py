####################################################################
#    MicroPython Driver for ESP32-C3 Supermini 0.42" OLED
#
#      See Readme.txt
####################################################################

from micropython import const
import framebuf
from font8x8 import font8
from font16x16 import font16

# register definitions
SET_NO_SCROLL       = const(0x2E)
SET_CONTRAST        = const(0x81)
SET_ENTIRE_ON       = const(0xA4)
SET_NORM_INV        = const(0xA6)
SET_DISP_OFF        = const(0xAE)
SET_DISP_ON         = const(0xAF)
SET_MEM_ADDR        = const(0x20)
SET_COL_ADDR        = const(0x21)
SET_PAGE_ADDR       = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP       = const(0xA0)
SET_MUX_RATIO       = const(0xA8)
SET_IREF_SELECT     = const(0xAD)
SET_COM_OUT_DIR     = const(0xC0)
SET_DISP_OFFSET     = const(0xD3)
SET_COM_PIN_CFG     = const(0xDA)
SET_DISP_CLK_DIV    = const(0xD5)
SET_PRECHARGE       = const(0xD9)
SET_VCOM_DESEL      = const(0xDB)
SET_CHARGE_PUMP     = const(0x8D)
#
WIDTH  = 72
HEIGHT = 40
BUF_LEN = WIDTH * HEIGHT // 8   # BUF_LEN = 360

class oled_72x40(framebuf.FrameBuffer):
    
    def __init__(self, i2c, rotation=0):
        self.i2c = i2c
        self.addr = 0x3C
        self.rotation = rotation % 4
        self.buffer = bytearray(BUF_LEN)
        self.temp = bytearray(2)
        self.write_list = [b"\x40", None]  # Co=0, D/C#=1
        super().__init__(self.buffer, WIDTH, HEIGHT, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        ''' display init -> datasheet '''
        for cmd in (
            SET_DISP_OFF,               # display off
            SET_DISP_CLK_DIV, 0x80,     # timing and driving scheme
            SET_MUX_RATIO, 0x3f,        # 0x3f = 64-1
            SET_DISP_OFFSET, 0x00,      #
            SET_DISP_START_LINE, 0x00,  # display RAM display start line = 0
            SET_CHARGE_PUMP, 0x14,      #
            SET_MEM_ADDR, 0x00,         # address setting
            SET_SEG_REMAP | 0x01,       # columns left -> right
            SET_COM_OUT_DIR | 0x08,     # lines top -> bottom
            SET_COM_PIN_CFG, 0x12,      # alternative COM pin configuration, Disable COM Left/Right remap
            SET_CONTRAST, 0xff,         # contrast to max
            SET_PRECHARGE, 0xf1,        #
            SET_VCOM_DESEL, 0x40,       #
            SET_NO_SCROLL,              # scrolling deactivation
            SET_ENTIRE_ON,              # output follows RAM content
            SET_NORM_INV,               # no bit inversion
            0x7f-11,                    # first line is 12 (or 0x40+12 ?)
            SET_DISP_ON                 # display on
        ):
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def write_cmd(self, cmd):
        ''' send command to display'''
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        ''' send data to display '''
        self.write_list[1] = buf
        self.i2c.writevto(self.addr, self.write_list)

    def poweroff(self):
        ''' display shutdown '''
        self.write_cmd(SET_DISP_OFF)

    def poweron(self):
        ''' display power up '''
        self.write_cmd(SET_DISP_ON)

    def invert(self, invert):
        ''' black <-> white invertion '''
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def rotate(self, rotate):
        ''' horizontal miror '''
        self.write_cmd(SET_COM_OUT_DIR | ((rotate & 1) << 3))
        self.write_cmd(SET_SEG_REMAP | (rotate & 1))

    def show(self):
        ''' render frame buffer '''
        for k in range(5):
            self.write_cmd(0x11)
            self.write_cmd(0x0e)
            self.write_cmd(0xb0 + k)
            self.write_data(self.buffer[72*k:72*k+72])
        
    def pixel_(self, x, y, c=1):
        ''' display (x,y) pixel '''
        xp, yp = self.framecoords(x, y)
        self.pixel(xp, yp, c)
    
    def hline_(self, x, y, w, c=1):
        ''' draw horizontal line '''
        xp, yp = self.framecoords(x, y)
        if self.rotation % 2 == 1:
            if self.rotation == 1: yp -= w
            self.vline(xp, yp, w, c)
        elif self.rotation == 2:
            self.hline(xp-w, yp, w, c)
        else:
            self.hline(xp, yp, w, c)
            
    def vline_(self, x, y, h, c=1):
        ''' draw vertical line '''
        xp, yp = self.framecoords(x, y)
        if self.rotation % 2 == 1:
            if self.rotation == 3: xp -= h
            self.hline(xp, yp, h, c)
        elif self.rotation == 2:
            self.vline(xp, yp-h, h, c)
        else:
            self.vline(xp, yp, h, c)
    
    def line_(self, x1, y1, x2, y2, c=1):
        ''' draw line '''
        xp1, yp1 = self.framecoords(x1, y1)
        xp2, yp2 = self.framecoords(x2, y2)
        self.line(xp1, yp1, xp2, yp2, c)
    
    def rect_(self, x, y, w, h, c=1, f=False):
        ''' draw rectangle
               f=True -> fill rectangle '''
        xp, yp = self.framecoords(x, y)
        if self.rotation == 1:
            self.rect(xp, yp-w, h, w, c, f)
        elif self.rotation == 3:
            self.rect(xp-h, yp, h, w, c, f)
        elif self.rotation == 2:
            self.rect(xp-w, yp-h, w, h, c, f)
        else:
            self.rect(xp, yp, w, h, c, f)
    
    def ellipse_(self, x, y, xr, yr, c=1, f=False, m=0b1111):
        ''' draw ellipse
               f=True -> fill ellipse
               m[bit q]=1 -> display quarter q'''                 
        xp, yp = self.framecoords(x, y)
        if self.rotation % 2 == 1:
            xr, yr = yr, xr
        self.ellipse(xp, yp, xr, yr, c, f, m)
    
    def clear(self, c=0):
        ''' erase screen '''
        self.fill(c)
        self.show()
    
    def framecoords(self, x, y):
        ''' display coords -> buffer coords '''
        if self.rotation == 0:
            xp, yp = x, y
        elif self.rotation == 1:
            xp, yp  = y, HEIGHT-x-1
        elif self.rotation == 2:
            xp, yp  = WIDTH-x-1, HEIGHT-y-1
        elif self.rotation == 3:
            xp, yp  = WIDTH-y-1, x
        return xp, yp

    def display_char8(self, char, x, y, c=1):
        ''' display 8 bit font character '''
        chlist = font8[ord(char) - 32]
        for n, byt in enumerate(chlist):
            j = n                 #  j = line nb
            for bit in range(8):  #  bit = col nb
                if ( byt >> bit) & 0x01:
                    self.pixel_(x + bit, y + j, c)

    def display_char16(self, char, x, y, c=1):
        ''' display 16 bit font character '''
        chlist = font16[ord(char) - 32]
        for n, byt in enumerate(chlist):
            j = n // 2                    # line nb
            for bit in range(8):
                i = (n % 2) * 8 + 8 - bit # col nb
                if ( byt >> bit) & 0x01:
                    self.pixel_(x + i, y + j, c)

    def text8(self, line, x, y, c=1):
        ''' display 8 bit font string '''
        for n, char in enumerate(line):
            self.display_char8(char, x + n*8, y, c)
    
    def text16(self, line, x, y, c=1):
        ''' display 16 bit font string '''
        for n, char in enumerate(line):
            self.display_char16(char, x + n*12, y, c)