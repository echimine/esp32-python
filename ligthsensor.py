from machine import ADC, Pin
from sensor import Sensor, SensorState
import json

class LightSensorWirings:
    def __init__(self, pin_adc):
        self.pin_adc = pin_adc

    @staticmethod
    def default():
        return LightSensorWirings(pin_adc=32)


class LightSensorState(SensorState):
    def __init__(self, raw=0, percent=0.0):
        self.raw = raw
        self.percent = percent

    def __str__(self):
        return "Light: raw={} percent={:.1f}%".format(
            self.raw, self.percent
        )
    
    def to_json(self):
        return json.dumps({
            "raw":self.raw,
            "percent":self.percent
        })


class LightSensor(Sensor):
    def __init__(
        self,
        wiring: LightSensorWirings,
        on_changed_fn=None,
        delta_trigger=0,
    ):
        self.wiring = wiring
        self.on_changed_fn = on_changed_fn
        self.delta_trigger = delta_trigger

        self.adc = ADC(Pin(self.wiring.pin_adc))
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)

        self.state = LightSensorState()
        self._last_raw = None

    def read(self) -> LightSensorState:
        raw = self.adc.read() 
        percent = (raw / 4095) * 100.0

        new_state = LightSensorState(raw=raw, percent=percent,)

        # 1er passage => déclenche direct (super utile pour debug)
        if self._last_raw is None:
            self.state = new_state
            self._last_raw = raw
            if self.on_changed_fn:
                self.on_changed_fn(self)
            return self.state

        # Sinon déclenche si variation suffisante
        percent_changed = abs(percent - self.state.percent) >= self.delta_trigger

        if percent_changed:
            self.state = new_state
            self._last_raw = raw
            if self.on_changed_fn:
                self.on_changed_fn(self)

        return self.state

