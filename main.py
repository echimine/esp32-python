import time
from joystick import *
from button import *

joystick = Joystick(JoystickWirings.default())
button = Button(ButtonWirings.default())
while True:
    bState = button.read()
    jState = joystick.read()
    print(jState)
    print(bState)
    time.sleep(0.2)
    