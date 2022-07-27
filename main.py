from machine import Pin, I2C, PWM
from ath20 import AHT20
from lcd import LCD, BL
from utime import sleep


def main():
    sensor = init_ath()
    screen = init_screen()
    screen.fill(screen.BLACK)
    loop(sensor, screen)


class ProgressIcon:
    def __init__(self, screen: LCD, x: int, y: int):
        self.position = 0
        self.x = x
        self.y = y
        self.base_col = 0xFFFF
        self.tick_col = 0xFF00

        self.coords = ((0, 0), (4, 0), (8, 0), (8, 4), (8, 8), (4, 8), (0, 8), (0, 4))
        for x_offset, y_offset in self.coords:
            screen.fill_rect(x + x_offset, y + y_offset, 3, 3, self.base_col)
        screen.show()

    def tick(self, screen: LCD):
        old_x_offset, old_y_offset = self.coords[self.position]
        self.position += 1
        if self.position == 8:
            self.position = 0
        x_offset, y_offset = self.coords[self.position]
        screen.fill_rect(self.x + old_x_offset, self.y + old_y_offset, 3, 3, self.base_col)
        screen.fill_rect(self.x + x_offset, self.y + y_offset, 3, 3, self.tick_col)


class Sensor:
    def __init__(self, history_len: int):
        self.history_len = history_len
        self.history = [-1] * history_len
        self.pointer = -1

    def update_pointer(self):
        self.pointer += 1
        if self.pointer == self.history_len:
            self.pointer = 0

    def update_value(self, value: float):
        self.update_pointer()
        # noinspection PyTypeChecker
        self.history[self.pointer] = value

    @property
    def value(self):
        return self.history[self.pointer]

    def print_to_screen(self, screen: LCD):
        raise NotImplementedError("Not implemented in base class")


class Temperature(Sensor):
    def __init__(self, history_len: int):
        super().__init__(history_len)

    def print_to_screen(self, screen: LCD):
        screen.fill_rect(2, 2, 120, 8, screen.BLACK)
        screen.text("Temp: %0.2f C" % self.value, 2, 2, screen.WHITE)


class Humidity(Sensor):
    def __init__(self, history_len: int):
        super().__init__(history_len)

    def print_to_screen(self, screen: LCD):
        screen.fill_rect(2, 20, 120, 8, screen.BLACK)
        screen.text("Humidity: %0.2f %%" % self.value, 2, 20, screen.WHITE)


def loop(sensor: AHT20, screen: LCD):
    progress = ProgressIcon(screen, 145, 2)
    temperature = Temperature(10)
    humidity = Humidity(10)
    while True:
        temperature.update_value(sensor.temperature)
        humidity.update_value(sensor.relative_humidity)
        temperature.print_to_screen(screen)
        humidity.print_to_screen(screen)
        progress.tick(screen)
        screen.show()
        sleep(1)


def init_ath() -> AHT20:
    """Initialise connection to ATH20"""
    i2c = I2C(0, scl=Pin(21), sda=Pin(20))
    return AHT20(i2c)


def init_screen() -> LCD:
    """Initialise LCD object."""
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)

    return LCD()


if __name__ == '__main__':
    main()
