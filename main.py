from joystick import *
from button import *
from orchestrator import *
from scanner import *
from wsclient import WSClient
from message import *
from machine import Pin
import neopixel
from time import sleep
from ledstripe import *
from ligthsensor import *

def on_connect(ws):
    print("WS connected")
    msg = Message(
        message_type=MessageType.DECLARATION,
        emitter="eliott",
        receiver="SERVER",
        value="hello je suis connecté"
    )
    ws.send(msg.to_json())

def on_message(msg):
    received = Message.from_json(msg)
    print("type:", received.message_type, "value:", received.value)

    if received.message_type != "RECEPTION_TEXT":
        return

    v = received.value

    # tente conversion en nombre
    try:
        percent = float(v)
    except:
        #print("pas un pourcentage:", v)
        return

    strip.bar(percent, color=(255, 0, 0))

def on_close(btn: Button):
    print(btn.state)
    print("WS closed")

ws = WSClient(
    "ws://192.168.4.230:9000",
    on_message=on_message,
    on_connect=on_connect,
    on_close=on_close
)

def on_button_clicked(btn):
    print(btn.state.to_json())
    print(btn.state.pressed)
    print("clické")
    msg = Message(
        message_type=ENVOI_TYPE.TEXT,
        emitter="eliott",
        receiver="ALL",
        value=btn.state.to_json()
    )
    ws.send(msg.to_json())

def on_click_joystick(joystick:Joystick):
    print(joystick.state.to_json())
    print(joystick.state.pressed)
    print("clické joystick")
    msg = Message(
        message_type=ENVOI_TYPE.TEXT,
        emitter="eliott",
        receiver="ALL",
        value=joystick.state.to_json()
    )
    ws.send(msg.to_json())

def on_card_detected(scanner:Scanner):
    print("Carte détectée :", scanner.state.uid)
    msg = Message(
        message_type=ENVOI_TYPE.TEXT,
        emitter="eliott",
        receiver="ALL",
        value=scanner.state.to_json()
    )
    ws.send(msg.to_json())
    
def on_led_strip_changed(ledStrip:LedStrip):
    print("ledStrip :", ledStrip.state)
    msg = Message(
        message_type=ENVOI_TYPE.TEXT,
        emitter="eliott",
        receiver="ALL",
        value=ledStrip.state.to_json()
    )
    ws.send(msg.to_json())

    
def on_light_changed(lightSensor:LightSensor):
    strip.bar(lightSensor.state.percent, color=(255, 0, 0))
    msg = Message(
        message_type=ENVOI_TYPE.TEXT,
        emitter="eliott",
        receiver="ALL",
        value=lightSensor.state.to_json()
    )
    ws.send(msg.to_json())


button = Button(ButtonWirings.default(), on_button_clicked)
joystick = Joystick(JoystickWirings.default(), on_clicked_button_function=on_click_joystick)
scanner = Scanner(ScannerWirings.default(), card_detected_fn=on_card_detected)
strip = LedStrip(LedStripWirings.default(), on_changed_fn=on_led_strip_changed)
light = LightSensor(LightSensorWirings.default(), on_changed_fn=on_light_changed)


o = Orchestrator(verbose=False) \
    .add_sensor(button) \
    .add_sensor(joystick) \
    .add_sensor(scanner).add_sensor(light)

while True:
    for _ in range(10):  # évite boucle infinie
        if ws.poll() is None:
            break


    o.update()
    #strip.rainbow(duration_ms=30, brightness=0.2, speed=2.0, step=5)

    #strip.rainbow()  # boucle infinie (Ctrl+C pour arrêter)

    # ou pendant 5 secondes
    #strip.rainbow(duration_ms=5000, brightness=0.2, speed=2.0, step=5)

