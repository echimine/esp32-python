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
            "is_detected":self.detected,
            "uid":self.uid
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
            cs=Pin(wiring.cs),
            rst=Pin(wiring.rst)
        )
 
        self.last_uid = None  # anti double-scan
        self.state = ScannerState()
 
    def read(self):
        stat, _ = self.reader.request(self.reader.REQIDL)

        # Pas de carte
        if stat != self.reader.OK:
            self.last_uid = None
            self.state = ScannerState(detected=False, uid=None)
            return self.state

        stat, raw_uid = self.reader.anticoll()
        if stat != self.reader.OK:
            self.state = ScannerState(detected=False, uid=None)
            return self.state

        uid = "-".join(map(str, raw_uid))

        # Carte détectée
        self.state = ScannerState(detected=True, uid=uid)

        # Anti spam : callback seulement si nouvelle carte
        if uid != self.last_uid:
            self.last_uid = uid
            if self.card_detected_fn:
                self.card_detected_fn(self)

        return self.state
