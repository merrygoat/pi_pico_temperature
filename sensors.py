import collections

from machine import I2C, Pin

from ext.aht.aht20 import AHT20
from ext.waveshare.lcd import LCD


class Sensor:
    def __init__(self, history_len: int):
        self.history_len = history_len
        self.history = collections.deque([], self.history_len)

    def update_value(self, value: float):
        self.history.appendleft(value)
        print(list(self.history))

    @property
    def value(self):
        return self.history[0]

    def print_to_screen(self, screen: LCD):
        raise NotImplementedError("Not implemented in base class")


class Temperature(Sensor):
    def __init__(self, history_len: int):
        super().__init__(history_len)

    def print_to_screen(self, screen: LCD):
        screen.fill_rect(2, 4, 110, 8, screen.BLACK)
        screen.text("Temp: %0.2f C" % self.value, 2, 4, screen.WHITE)


class Humidity(Sensor):
    def __init__(self, history_len: int):
        super().__init__(history_len)

    def print_to_screen(self, screen: LCD):
        screen.fill_rect(2, 22, 120, 8, screen.BLACK)
        screen.text("Humidity: %0.2f %%" % self.value, 2, 22, screen.WHITE)


def sample_sensor(sensor: AHT20, temperature: sensors.Temperature, humidity: sensors.Humidity):
    temperature.update_value(round(sensor.temperature, 2))
    humidity.update_value(round(sensor.relative_humidity, 2))


def init_ath() -> AHT20:
    """Initialise connection to ATH20"""
    i2c = I2C(0, scl=Pin(21), sda=Pin(20))
    return AHT20(i2c)
