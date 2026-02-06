# accelerometre.py
from machine import Pin, I2C
from sensor import *
import json
from time import sleep


class AccelerometreWirings:
    def __init__(self, scl_pin: int, sda_pin: int, i2c_id: int = 0, freq: int = 100000, addr: int = 0x68):
        self.scl_pin = scl_pin
        self.sda_pin = sda_pin
        self.i2c_id = i2c_id
        self.freq = freq
        self.addr = addr

    @staticmethod
    def default():
        # ESP32 classique
        return AccelerometreWirings(
            scl_pin=22,
            sda_pin=21,
            i2c_id=0,
            freq=100000,   # plus stable
            addr=0x68
        )


class AccelerometreState(SensorState):
    def __init__(self, x=0, y=0, z=0):
        self.x = x  # int16
        self.y = y
        self.z = z

    def __str__(self):
        return "Accel(raw): x={} y={} z={}".format(self.x, self.y, self.z)

    def to_json(self):
        return json.dumps({
            "x": self.x,
            "y": self.y,
            "z": self.z
        })


class Accelerometre(Sensor):
    """
    MPU-6050 (0x68)
    - Lecture brute int16
    - Valeurs comprises entre -32768 et 32767
    """
    _REG_PWR_MGMT_1 = 0x6B
    _REG_ACCEL_XOUT_H = 0x3B

    def __init__(self, wiring: AccelerometreWirings, on_changed_fn=None):
        self.wiring = wiring
        self.on_changed_fn = on_changed_fn

        self.i2c = I2C(
            wiring.i2c_id,
            scl=Pin(wiring.scl_pin),
            sda=Pin(wiring.sda_pin),
            freq=wiring.freq
        )
        self.addr = wiring.addr

        self.state = AccelerometreState()

        # Wake up MPU6050
        self._write(self._REG_PWR_MGMT_1, 0x00)
        sleep(0.05)

    def _write(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg, bytes([val]))

    def _read(self, reg, n):
        return self.i2c.readfrom_mem(self.addr, reg, n)

    def _s16(self, msb, lsb):
        v = (msb << 8) | lsb
        return v - 65536 if v & 0x8000 else v

    def read(self):
        try:
            data = self._read(self._REG_ACCEL_XOUT_H, 6)
        except OSError:
            # bus glitch → on garde l'ancien state
            return self.state

        x = self._s16(data[0], data[1])
        y = self._s16(data[2], data[3])
        z = self._s16(data[4], data[5])

        new_state = AccelerometreState(x=x, y=y, z=z)
        self.state = new_state

        if self.on_changed_fn:
            self.on_changed_fn(self)

        return new_state
