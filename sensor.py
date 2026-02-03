class SensorState:
    def __str__(self):
        pass

    def to_json(self):
        pass

class Sensor:
    state: SensorState

    def read(self):
        pass

