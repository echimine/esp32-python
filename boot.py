# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
print("in boot")
import network
import time

ssid = 'Salle-de-creation'
password = 'animation'

def wifi_connect(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Try connect to SSID : {ssid}")
        wlan.connect(ssid, password)

        while not wlan.isconnected():
            print('.', end = " ")
            time.sleep_ms(500)

    print("\nWi-Fi Config: ", wlan.ifconfig())

wifi_connect(ssid, password)