from machine import Pin
import time

class SonarWirings:
    
    def __init__(self, pinTrig, pinEcho):
        self.pinTrig = pinTrig
        self.pinEcho = pinEcho
    
    @staticmethod
    def default():
        return SonarWirings(pinTrig=5, pinEcho=18)


class SonarState:    
    
    def __init__(self, distance=0):
        self.distance = distance
    
    def __str__(self):
        return "Distance: {} cm".format(self.distance)

class Sonar:
    
    def __init__(self, wiring:SonarWirings):
        # Trigger pin (output)
        self.trig = Pin(wiring.pinTrig, Pin.OUT)
        
        # Echo pin (input)
        self.echo = Pin(wiring.pinEcho, Pin.IN)
        
        # Initialize trigger to low
        self.trig.value(0)
    
    def read(self):
        # Send a 10us pulse to trigger
        self.trig.value(0)
        time.sleep_us(2)
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)
        
        # Wait for echo to go high
        timeout = 30000  # 30ms timeout
        start = time.ticks_us()
        while self.echo.value() == 0:
            if time.ticks_diff(time.ticks_us(), start) > timeout:
                return SonarState(distance=-1)  # Timeout error
            pulse_start = time.ticks_us()
        
        # Wait for echo to go low
        start = time.ticks_us()
        while self.echo.value() == 1:
            if time.ticks_diff(time.ticks_us(), start) > timeout:
                return SonarState(distance=-1)  # Timeout error
            pulse_end = time.ticks_us()
        
        # Calculate distance
        pulse_duration = time.ticks_diff(pulse_end, pulse_start)
        # Speed of sound is 343 m/s or 0.0343 cm/us
        # Distance = (time * speed) / 2 (round trip)
        distance = (pulse_duration * 0.0343) / 2
        
        return SonarState(distance=distance)
    
