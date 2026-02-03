from machine import Pin
import neopixel
from sensor import *
import time


class LedStripWirings:
    def __init__(self, data_pin: int, led_count: int):
        self.data_pin = data_pin
        self.led_count = led_count

    @staticmethod
    def default():
        # Adapte si besoin : pin 13, 153 leds
        return LedStripWirings(data_pin=13, led_count=153)


class LedStripState(SensorState):
    def __init__(self, is_on=False, color=(0, 0, 0), brightness=1.0):
        self.is_on = is_on
        self.color = color  # (r,g,b) "requested" color
        self.brightness = brightness  # 0.0 -> 1.0

    def __str__(self):
        return "On: {}, Color: {}, Brightness: {}".format(
            self.is_on, self.color, self.brightness
        )


class LedStrip(Sensor):
    def __init__(self, wiring: LedStripWirings, on_changed_fn=None):
        self.wiring = wiring
        self.on_changed_fn = on_changed_fn

        self.pin = Pin(wiring.data_pin, Pin.OUT)
        self.np = neopixel.NeoPixel(self.pin, wiring.led_count)

        # State interne
        self._is_on = False
        self._color = (0, 0, 0)
        self._brightness = 1.0

        # Ensure off at start
        self.clear()

    def flash_led(self, index, color, duration_ms=120):
        """
        Allume une LED puis l’éteint après duration_ms.
        ⚠️ Bloquant pendant duration_ms
        """
        if index < 0 or index >= self.wiring.led_count:
            return

        prev = self.np[index]

        self.np[index] = self._apply_brightness(*color)
        self.np.write()

        time.sleep_ms(duration_ms)

        self.np[index] = prev
        self.np.write()

    # ---------- helpers ----------
    def _apply_brightness(self, r, g, b):
        # clamp brightness and rgb
        br = self._brightness
        if br < 0:
            br = 0.0
        elif br > 1:
            br = 1.0

        r = int(max(0, min(255, r)) * br)
        g = int(max(0, min(255, g)) * br)
        b = int(max(0, min(255, b)) * br)
        return (r, g, b)

    def _emit_changed(self):
        if self.on_changed_fn:
            self.on_changed_fn(self.read())

    # ---------- public api ----------
    def set_brightness(self, brightness: float):
        self._brightness = brightness
        # re-apply current color to the whole strip if currently on
        if self._is_on:
            self.fill(*self._color)
        else:
            self._emit_changed()

    def fill(self, r, g, b):
        """Fill whole strip with a color (respects brightness)."""
        self._is_on = True
        self._color = (r, g, b)

        c = self._apply_brightness(r, g, b)
        for i in range(self.wiring.led_count):
            self.np[i] = c
        self.np.write()

        self._emit_changed()

    def clear(self):
        """Turn off all leds."""
        self._is_on = False
        self._color = (0, 0, 0)

        for i in range(self.wiring.led_count):
            self.np[i] = (0, 0, 0)
        self.np.write()

        self._emit_changed()

    def set_pixel(self, index: int, r, g, b, auto_write=True):
        """Set one led (0..N-1)."""
        if index < 0 or index >= self.wiring.led_count:
            return  # or raise ValueError

        self._is_on = True  # if you set a pixel, strip is considered "on"
        c = self._apply_brightness(r, g, b)
        self.np[index] = c

        if auto_write:
            self.np.write()
            self._emit_changed()
            
    def bar(self, percent, color=(255, 0, 0), bg=(0, 0, 0), auto_write=True):
        # clamp 0..100
        if percent < 0:
            percent = 0
        elif percent > 100:
            percent = 100

        n = self.wiring.led_count
        n_on = int((percent * n) / 100)

        # applique brightness
        c_on = self._apply_brightness(*color)
        c_off = self._apply_brightness(*bg)

        # on considère "on" si au moins une LED est allumée
        self._is_on = n_on > 0
        self._color = color  # couleur "demandée" (non-brightness)

        for i in range(n):
            self.np[i] = c_on if i < n_on else c_off

        if auto_write:
            self.np.write()
            self._emit_changed()



    def rainbow(self, speed=1.4, step=4, brightness=None, sleep_ms=10, duration_ms=None):
        """
        Lance un arc-en-ciel animé.
        - speed: vitesse (1.0 normal, 2.0 plus rapide)
        - step: écart de teinte entre leds (plus grand = arc-en-ciel plus serré)
        - brightness: 0.0..1.0 (optionnel)
        - sleep_ms: pause entre frames (8-20ms conseillé)
        - duration_ms: si None => boucle infinie, sinon stop après duration_ms
        """
        if brightness is not None:
            self._brightness = brightness

        n = self.wiring.led_count
        hue = 0
        start = time.ticks_ms()

        try:
            while True:
                # stop si durée demandée
                if duration_ms is not None:
                    if time.ticks_diff(time.ticks_ms(), start) >= duration_ms:
                        break

                # dessine une frame
                base = hue & 255
                for i in range(n):
                    h = (base + i * step) & 255
                    r, g, b = self._wheel(h)
                    self.np[i] = self._apply_brightness(r, g, b)
                self.np.write()

                # avance la teinte (vitesse)
                # 1 incrément par frame ~ OK, on scale avec speed
                hue = (hue + max(1, int(speed))) & 255

                time.sleep_ms(sleep_ms)

        except KeyboardInterrupt:
            # permet d'arrêter proprement si boucle infinie
            pass

    def _wheel(self, pos):
        """0..255 -> (r,g,b) arc-en-ciel NeoPixel classique."""
        pos = 255 - (pos & 255)
        if pos < 85:
            return (255 - pos * 3, 0, pos * 3)
        if pos < 170:
            pos -= 85
            return (0, pos * 3, 255 - pos * 3)
        pos -= 170
        return (pos * 3, 255 - pos * 3, 0)


    def show(self):
        """Write current buffer to strip (manual flush)."""
        self.np.write()
        self._emit_changed()

    def read(self):
        """Return a state snapshot (like your Scanner)."""
        return LedStripState(
            is_on=self._is_on,
            color=self._color,
            brightness=self._brightness
        )
