from machine import Pin, ADC
from sensor import *

class JoystickWirings:

    def __init__(self, pinX, pinY, pinButton):
        self.pinX = pinX
        self.pinY = pinY
        self.pinButton = pinButton

    @staticmethod
    def default():
        return JoystickWirings(pinX=34, pinY=35, pinButton=25)


class JoystickState(SensorState):    
    
    def __init__(self, x=0, y=0, button=False):
        self.x = x
        self.y = y
        self.button = button

    def __str__(self):
        return "X: {}, Y: {}, Button: {}".format(self.x, self.y, self.button)

class Joystick(Sensor):

    def __init__(self, wiring:JoystickWirings):
        # Axes
        self.x = ADC(Pin(wiring.pinX))
        self.y = ADC(Pin(wiring.pinY))

        # Config ADC
        self.x.atten(ADC.ATTN_11DB)
        self.y.atten(ADC.ATTN_11DB)
        self.x.width(ADC.WIDTH_12BIT)
        self.y.width(ADC.WIDTH_12BIT)

        # Bouton
        self.btn = Pin(wiring.pinButton, Pin.IN, Pin.PULL_UP)

    def read(self):
        x_val = self.x.read()
        y_val = self.y.read()
        btn_val = not self.btn.value()  # Invert because button is active low
        return JoystickState(x_val, y_val, btn_val)    
    

