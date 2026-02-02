
from joystick import *
from button import *
from orchestrator import *

def on_clicked_buton():
    print("Clicked")

button = Button(ButtonWirings.default(), on_clicked_function=on_clicked_buton)
joystick = Joystick(JoystickWirings.default())

o = Orchestrator(verbose=False).add_sensor(button).add_sensor(joystick)

while True:
    o.update()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

