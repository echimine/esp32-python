from machine import ADC, Pin
from sensor import Sensor, SensorState


class LightSensorWirings:
    def __init__(self, pin_adc):
        self.pin_adc = pin_adc

    @staticmethod
    def default():
        return LightSensorWirings(pin_adc=32)


class LightSensorState(SensorState):
    def __init__(self, raw=0, percent=0.0, is_dark=False):
        self.raw = raw
        self.percent = percent
        self.is_dark = is_dark

    def __str__(self):
        return "Light: raw={} percent={:.1f}% dark={}".format(
            self.raw, self.percent, self.is_dark
        )


class LightSensor(Sensor):
    def __init__(
        self,
        wiring: LightSensorWirings,
        on_changed_fn=None,
        dark_threshold=1200,
        delta_trigger=0,
    ):
        self.wiring = wiring
        self.on_changed_fn = on_changed_fn
        self.dark_threshold = dark_threshold
        self.delta_trigger = delta_trigger

        self.adc = ADC(Pin(self.wiring.pin_adc))
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)

        self.state = LightSensorState()
        self._last_raw = None

    def read(self) -> LightSensorState:
        raw = self.adc.read()  # 0..4095
        percent = (raw / 4095) * 100.0
        is_dark = raw < self.dark_threshold

        new_state = LightSensorState(raw=raw, percent=percent, is_dark=is_dark)

        # 1er passage => déclenche direct (super utile pour debug)
        if self._last_raw is None:
            self.state = new_state
            self._last_raw = raw
            if self.on_changed_fn:
                self.on_changed_fn(self.state)
            return self.state

        # Sinon déclenche si variation suffisante ou changement sombre/lumineux
        raw_changed = abs(raw - self._last_raw) >= self.delta_trigger
        mode_changed = (new_state.is_dark != self.state.is_dark)

        if raw_changed or mode_changed:
            self.state = new_state
            self._last_raw = raw
            if self.on_changed_fn:
                self.on_changed_fn(self.state)

        return self.state
