from machine import Pin, time_pulse_us
from sensor import Sensor, SensorState
import time
 
# =========================
# Wiring
# =========================
class SonarWirings:
    def __init__(self, pinTrig, pinEcho):
        self.pinTrig = pinTrig
        self.pinEcho = pinEcho
 
    @staticmethod
    def default():
        return SonarWirings(pinTrig=33, pinEcho=25)
 
 
# =========================
# State
# =========================
class SonarState(SensorState):
    def __init__(self, distance_cm=0.0):
        self.distance_cm = distance_cm
 
    def __str__(self):
        return "Distance: {}cm".format(self.distance_cm)
 
    def to_json(self):
        return '{{ "distance_cm": {} }}'.format(self.distance_cm)
 
 
# =========================
# Sensor
# =========================
class Sonar(Sensor):
    def __init__(self, wiring: SonarWirings, on_read_fn=None):
        super().__init__()
        self.trig = Pin(wiring.pinTrig, Pin.OUT)
        self.echo = Pin(wiring.pinEcho, Pin.IN)
        self.state = SonarState()
        self.on_read_fn = on_read_fn
        self._last_read = 0
 
    def read(self):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_read) < 100:  # 10 lectures/sec max
            return self.state
 
        self._last_read = now
 
        try:
            # Envoie une impulsion TRIG de 10µs
            self.trig.value(0)
            time.sleep_us(2)
            self.trig.value(1)
            time.sleep_us(10)
            self.trig.value(0)
 
            # Mesure la durée du signal ECHO
            duration = time_pulse_us(self.echo, 1, 30000)  # timeout 30ms
 
            if duration < 0:
                raise Exception("Timeout ECHO")
 
            # Conversion en cm : vitesse du son = 343 m/s
            distance_cm = (duration / 2) / 29.1
 
            self.state = SonarState(round(distance_cm, 1))
 
            if self.on_read_fn:
                self.on_read_fn(self)
 
            return self.state
 
        except Exception as e:
            print("❌ Exception Sonar:", type(e).__name__, e)
            self.state = SonarState()
            return self.state