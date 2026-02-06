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
from accelerometre import *
import json


def on_connect(ws):
    print("WS connected")
    msg = Message(
        message_type=MessageType.DECLARATION,
        emitter="ESP32_ELIOTT",
        receiver="SERVER",
        value="hello je suis connecté"
    )
    ws.send(msg.to_json())



def on_message(msg):
    received = Message.from_json(msg)

    mtype = received.message_type
    emitter = received.emitter
    receiver = received.receiver
    sensor_id = getattr(received, "sensor_id", None)
    value = received.value

    print("type:", mtype, "sensor:", sensor_id, "value:", value)

    # ----------------------------
    # OTHER
    # ----------------------------
    if mtype == "DECLARATION":
        print("📢 Device connected:", emitter)
        return

    if mtype == "SYS_MESSAGE":
        print("🖥️ System:", value)
        return

    if mtype == "WARNING":
        print("⚠️ Warning:", value)
        return

    # ----------------------------
    # TEXT
    # ----------------------------
    if mtype in ("RECEPTION_TEXT", "ENVOI_TEXT"):
        recv = (receiver or "").strip().upper()
        emit = (emitter or "").strip()

        print("DEBUG emit=", repr(emit), "recv=", repr(receiver), "recv_norm=", repr(recv))

        if recv == "ALL":
            print(f"📢 {emit} → ALL : {value}")
            strip.flash_led(153, (255,0,255))
            strip.show()
            
        elif recv == "":
            print(f"❓ receiver vide (broadcast/serveur?) | {emit} → ??? : {value}")
        else:
            print(f"📩 {emit} → {receiver} : {value}")
            strip.flash_led(153, (255,111,255))
            strip.show()
        return

    if mtype == "RECEPTION_CLIENT_LIST":
        print("👥 Clients connectés:", value)
        return



    # ----------------------------
    # MEDIA
    # ----------------------------
    if mtype in ("RECEPTION_IMAGE", "ENVOI_IMAGE"):
        print("🖼️ Image received")
        return

    if mtype in ("RECEPTION_AUDIO", "ENVOI_AUDIO"):
        print("🔊 Audio received")
        return

    # ----------------------------
    # SENSOR
    # ----------------------------
    # SENSOR
    if mtype in ("RECEPTION_SENSOR", "ENVOI_SENSOR"):
        if not sensor_id:
            print("❌ Sensor message without sensor_id")
            return

        # ---- FIX IMPORTANT ----
        if isinstance(value, str):
            try:
                data = json.loads(value)
            except:
                print("❌ Invalid sensor JSON:", value)
                return
        else:
            data = value  # déjà un dict
        # -----------------------

        print("DATA SENSOR:", data)

        if sensor_id == "LED":
            led_id = data.get("led_id")
            state = data.get("state")
            strip.flash_led(led_id -1, (255,255,255))
            strip.show()
            return
        
        if sensor_id == "TEMPERATURE":
            temperature = data.get("temperature")
            humidty = data.get("humidity")
            if temperature > 37:
                strip.flash_led(110, (255,0,0))
                strip.show()
            if temperature < 37:
                strip.flash_led(110, (255,255,0))
                strip.show()
            return
    
        if sensor_id == "ACCELEROMETER":
            x = data.get("x", 0.0)
            y = data.get("y", 0.0)
            z = data.get("z", 0.0)
            state = data.get("state")
    
            if state == 1:
                strip.flash_led(150, (255,200,110))
            if state == 2:
                strip.flash_led(151, (255,200,110))
            if state == 3:
                strip.flash_led(152, (255,200,110))
            else:
                 strip.flash_led(153, (255,200,110))
            #strip.from_accelerometer(x, y, z)
            #x_norm = x / 32767   # -> -1.0 .. +1.0

            #strip.bar_from_axis(x_norm, color=(255, 255, 0))  # jaune©
            return
        
        
        if sensor_id == "LIGHT":
            percent = data.get("percentage", 0)
            #strip.bar(percent, color=(255, 0, 0))
            return

        print("❓ Unknown sensor:", sensor_id)
        return

    # ----------------------------
    print("❓ Unknown message type:", mtype)
    return 


def on_close(btn: Button):
    print(btn.state)
    print("WS closed")

#ws://192.168.1.133:8765
#"ws://192.168.4.230:9000"
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
        emitter="ESP32_ELIOTT",
        receiver="ALL",
        value=btn.state.to_json()
    )
    #ws.send(msg.to_json())

def on_click_joystick(joystick:Joystick):
    print(joystick.state.to_json())
    print(joystick.state.pressed)
    print("clické joystick")
    msg = Message(
        message_type=ENVOI_TYPE.TEXT,
        emitter="ESP32_ELIOTT",
        receiver="ALL",
        value=joystick.state.to_json()
    )
    #ws.send(msg.to_json())

def on_card_detected(scanner:Scanner):
    print("Carte détectée :", scanner.state.uid)
    msg = Message(
        message_type=ENVOI_TYPE.TEXT,
        emitter="ESP32_ELIOTT",
        receiver="ALL",
        value=scanner.state.to_json()
    )
    #ws.send(msg.to_json())
    
def on_led_strip_changed(ledStrip:LedStrip):
    #print("ledStrip :", ledStrip.state)
    msg = Message(
        message_type=ENVOI_TYPE.TEXT,
        emitter="ESP32_ELIOTT",
        receiver="ALL",
        value=ledStrip.state.to_json()
    )
    #ws.send(msg.to_json())

    
def on_light_changed(lightSensor:LightSensor):
    #strip.bar(lightSensor.state.percent, color=(255, 0, 0))
    msg = Message(
        MessageType.ENVOI.SENSOR,emitter="ESP32_ELIOTT", receiver="ESP32_NATHAN", sensor_id=SensorId.LIGHT,value=lightSensor.state.to_json()
    )
    #ws.send(msg.to_json())
    
    
def on_accelero_changed(accelerometre: Accelerometre):
    x = accelerometre.state.x
    y = accelerometre.state.y
    z = accelerometre.state.z
    accepted_ranges = {
        (0,10000): 1,
        (10000,20000): 2,
        (20000,30000): 3,
    }
    
    value = get_state_accepted_ranges(x,accepted_ranges)
    
    response = json.dumps({
        "state":value
    })
    
        
    print(accelerometre.state)
    msg = Message(
        MessageType.ENVOI.SENSOR,emitter="ESP32_ELIOTT", receiver="ALL", sensor_id=SensorId.ACCELEROMETER,value=response
    )
    ws.send(msg.to_json())

def get_state_accepted_ranges(x, accepted_ranges):
    for k in accepted_ranges.keys():
        if k[0] <= x <= k[1]:
            return accepted_ranges[k]
        
def get_items_by_value():
    pass

button = Button(ButtonWirings.default(), on_button_clicked)
joystick = Joystick(JoystickWirings.default(), on_clicked_button_function=on_click_joystick)
scanner = Scanner(ScannerWirings.default(), card_detected_fn=on_card_detected)
strip = LedStrip(LedStripWirings.default(), on_changed_fn=on_led_strip_changed)
light = LightSensor(LightSensorWirings.default(), on_changed_fn=on_light_changed)
accel = Accelerometre(AccelerometreWirings.default(), on_changed_fn=on_accelero_changed)

o = Orchestrator(verbose=False) \
    .add_sensor(button) \
    .add_sensor(joystick) \
    .add_sensor(scanner) \
    .add_sensor(light) \
    .add_sensor(accel) 

while True:
    for _ in range(10):  # évite boucle infinie
        if ws.poll() is None:
            break
    o.update()
    #strip.rainbow(duration_ms=30, brightness=0.2, speed=2.0, step=5)

    #strip.rainbow()  # boucle infinie (Ctrl+C pour arrêter)

    # ou pendant 5 secondes
    #strip.rainbow(duration_ms=5000, brightness=0.2, speed=2.0, step=5)

