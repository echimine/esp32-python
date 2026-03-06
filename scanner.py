from machine import Pin, SPI
from mfrc522 import MFRC522
from sensor import *
import json
 
 
class ScannerWirings:
    def __init__(self, cs, sck, mosi, miso, rst):
        self.cs = cs
        self.sck = sck
        self.mosi = mosi
        self.miso = miso
        self.rst = rst
 
    @staticmethod
    def default():
        return ScannerWirings(
            cs=5,
            sck=18,
            mosi=4,
            miso=19,
            rst=22
        )
 
 
class ScannerState(SensorState):
    def __init__(self, detected=False, uid=None):
        self.detected = detected
        self.uid = uid
 
    def __str__(self):
        return "Detected: {}, UID: {}".format(self.detected, self.uid)
    

    def to_json(self):
        return json.dumps({
            "isdetected":self.detected,
        })
 
 
class Scanner(Sensor):
 
    def __init__(self, wiring: ScannerWirings, card_detected_fn=None):
        self.card_detected_fn = card_detected_fn
 
        self.spi = SPI(
            2,
            baudrate=1_000_000,
            polarity=0,
            phase=0,
            sck=Pin(wiring.sck),
            mosi=Pin(wiring.mosi),
            miso=Pin(wiring.miso)
        )
 
        self.reader = MFRC522(
            spi=self.spi,
            cs=Pin(wiring.cs, Pin.OUT),
            rst=Pin(wiring.rst, Pin.OUT)
        )
 
        self.last_uid = None  # anti double-scan
        self.state = ScannerState()
 
    def read(self):
        stat, _ = self.reader.request(self.reader.REQIDL)

        detected = stat == self.reader.OK

        # changement d'état seulement
        if detected != self.state.detected:
            self.state = ScannerState(detected=detected, uid=None)

            if detected and self.card_detected_fn:
                self.card_detected_fn(self)

        return self.state
