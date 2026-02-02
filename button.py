from machine import Pin
from sensor import *

class ButtonWirings:
    
    def __init__(self, pinButton):
        self.pinButton = pinButton
    
    @staticmethod
    def default():
        return ButtonWirings(pinButton=26)


class ButtonState(SensorState):    
    
    def __init__(self, pressed=False):
        self.pressed = pressed
    
    def __str__(self):
        return "Button: {}".format(self.pressed)

class Button(Sensor):
    
    def __init__(self, wiring:ButtonWirings, on_clicked_function= None):
        self.btn = Pin(wiring.pinButton, Pin.IN, Pin.PULL_UP)
        self.on_clicked_function = on_clicked_function
    
    def read(self):
        pressed = not self.btn.value()
        
        if(pressed):
            self.on_clicked_function()
    
        return ButtonState(pressed=pressed)
    

