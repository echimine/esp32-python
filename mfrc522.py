from machine import Pin
import time
 
 
class MFRC522:
 
    OK = 0
    NOTAGERR = 1
    ERR = 2
 
    REQIDL = 0x26
    REQALL = 0x52
 
    def __init__(self, spi, cs, rst):
        self.spi = spi
        self.cs = cs
        self.rst = rst
 
        self.cs.init(Pin.OUT, value=1)
        self.rst.init(Pin.OUT, value=1)
 
        self.reset()
        self.init()
 
    def write_reg(self, reg, val):
        self.cs.value(0)
        self.spi.write(bytearray([(reg << 1) & 0x7E, val]))
        self.cs.value(1)
 
    def read_reg(self, reg):
        self.cs.value(0)
        self.spi.write(bytearray([((reg << 1) & 0x7E) | 0x80]))
        val = self.spi.read(1)
        self.cs.value(1)
        return val[0]
 
    def set_bitmask(self, reg, mask):
        self.write_reg(reg, self.read_reg(reg) | mask)
 
    def clear_bitmask(self, reg, mask):
        self.write_reg(reg, self.read_reg(reg) & (~mask))
 
    def reset(self):
        self.write_reg(0x01, 0x0F)
 
    def init(self):
        self.reset()
        self.write_reg(0x2A, 0x8D)
        self.write_reg(0x2B, 0x3E)
        self.write_reg(0x2D, 30)
        self.write_reg(0x2C, 0)
        self.write_reg(0x15, 0x40)
        self.write_reg(0x11, 0x3D)
        self.antenna_on()
 
    def antenna_on(self):
        if not (self.read_reg(0x14) & 0x03):
            self.set_bitmask(0x14, 0x03)
 
    def to_card(self, command, send_data):
        back_data = []
        back_len = 0
        status = self.ERR
 
        irq_en = 0x00
        wait_irq = 0x00
 
        if command == 0x0E:
            irq_en = 0x12
            wait_irq = 0x10
        elif command == 0x0C:
            irq_en = 0x77
            wait_irq = 0x30
 
        self.write_reg(0x02, irq_en | 0x80)
        self.clear_bitmask(0x04, 0x80)
        self.set_bitmask(0x0A, 0x80)
        self.write_reg(0x01, 0x00)
 
        for d in send_data:
            self.write_reg(0x09, d)
 
        self.write_reg(0x01, command)
 
        if command == 0x0C:
            self.set_bitmask(0x0D, 0x80)
 
        i = 2000
        while i > 0:
            n = self.read_reg(0x04)
            i -= 1
            if n & 0x01 or n & wait_irq:
                break
 
        self.clear_bitmask(0x0D, 0x80)
 
        if i == 0:
            return self.ERR, None, 0
 
        if self.read_reg(0x06) & 0x1B:
            return self.ERR, None, 0
 
        status = self.OK
 
        if command == 0x0C:
            n = self.read_reg(0x0A)
            last_bits = self.read_reg(0x0C) & 0x07
            if last_bits:
                back_len = (n - 1) * 8 + last_bits
            else:
                back_len = n * 8
 
            for _ in range(n):
                back_data.append(self.read_reg(0x09))
 
        return status, back_data, back_len
 
    def request(self, mode):
        self.write_reg(0x0D, 0x07)  # 7 bits framing
        status, back_data, back_len = self.to_card(0x0C, [mode])
 
        if status != self.OK or back_len != 0x10:
            return self.ERR, None
 
        return self.OK, back_data
 
    def anticoll(self):
        self.write_reg(0x0D, 0x00)
 
        status, back_data, back_len = self.to_card(0x0C, [0x93, 0x20])
 
        if status != self.OK or len(back_data) != 5:
            return self.ERR, None
 
        checksum = 0
        for i in range(4):
            checksum ^= back_data[i]
 
        if checksum != back_data[4]:
            return self.ERR, None
 
        return self.OK, back_data[:4]