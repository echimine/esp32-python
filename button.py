from machine import Pin

class ButtonWirings:
    
    def __init__(self, pinButton):
        self.pinButton = pinButton
    
    @staticmethod
    def default():
        return ButtonWirings(pinButton=26)


class ButtonState:    
    
    def __init__(self, pressed=False):
        self.pressed = pressed
    
    def __str__(self):
        return "Button: {}".format(self.pressed)

class Button:
    
    def __init__(self, wiring:ButtonWirings):
        self.btn = Pin(wiring.pinButton, Pin.IN, Pin.PULL_UP)
    
    def read(self):
        btn_val = not self.btn.value()
        return ButtonState(pressed=btn_val)
    

