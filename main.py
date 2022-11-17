from time import sleep
from machine import Pin, I2C, PWM
import framebuf

import wifi
from ext.ath20 import AHT20
from ext.lcd import LCD, BL
from progress import ProgressIcon
import micropython
import gc
micropython.mem_info()


class Image:
    valid_modes = [0, 1]  # 0 = Greyscale, 1 = BRG556

    def __init__(self, filename: str):
        self.data = []
        self.format = ""
        self.width = 0
        self.height = 0
        self.mode = ""
        self._load_image(filename)

    def _load_image(self, filename: str):
        """Assumes data are space delimited integers. First letter indicates image format, second indicates number of
        pixels per row, third indicates number of rows. Following integers are pixel values."""
        micropython.mem_info()
        gc.collect()
        micropython.mem_info()
        with open(filename, 'rb') as input_file:
            self.data = input_file.read()

        self.mode = self.data[0]
        if self.mode not in self.valid_modes:
            raise SyntaxError("Error reading image from '{filename}'. Invalid image mode.")
        self.width = int(self.data[1])
        self.height = int(self.data[2])
        self.data = [int(x) for x in self.data[3:]]
        if len(self.data) != self.width * self.height:
            raise SyntaxError("Error reading image from '{filename}'. Number of pixels doe not match width and height.")

    def get_framebuffer(self) -> framebuf.FrameBuffer:
        if self.mode == 0:
            self._greyscale_to_colour()

        buffer = framebuf.FrameBuffer(bytearray(self.height * self.width * 2), self.width, self.height, framebuf.RGB565)
        for x in range(self.width):
            for y in range(self.height):
                buffer.pixel(x, y, self.data[x + y * self.width])
        return buffer

    def _greyscale_to_colour(self):
        """Convert an 8 bit greyscale image to RGB 565."""
        greyscale = self.data
        self.data = [(pixel << 8) | (pixel << 3) | (pixel >> 2) for pixel in greyscale]


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


def loop(sensor: AHT20, screen: LCD, wlan: wifi.StatefulWLAN):
    progress = ProgressIcon(screen, 145, 2)
    temperature = Temperature(10)
    humidity = Humidity(10)
    wifi_image = Image("images/wifi_large.bin")
    print("Loop initialised")
    print(type(wlan))

    time = 0
    while True:
        print(f"Tick {time}")
        if time % 1 == 0:
            sample_temperature(sensor, screen, temperature, humidity, progress)
        if time % 10 == 0:
            check_wifi(wlan, screen, wifi_image)
        time += 1
        if time == 10:
            time = 0
        sleep(1)


def check_wifi(wlan: wifi.StatefulWLAN, screen: LCD, wifi_icon: Image):
    status = wlan.status()
    print(f"Wifi status: {status}")
    if wlan.status() != wlan.previous_status:
        if status == 3:
            screen.blit(wifi_icon.get_framebuffer(), 50, 50)
            screen.show()
        else:
            wlan.disconnect()
            wlan.connect()
    wlan.previous_status = status


def sample_temperature(sensor: AHT20, screen: LCD, temperature: Temperature, humidity: Humidity,
                       progress: ProgressIcon):
    temperature.update_value(sensor.temperature)
    humidity.update_value(sensor.relative_humidity)
    temperature.print_to_screen(screen)
    humidity.print_to_screen(screen)
    progress.tick(screen)
    screen.show()


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


def load_config() -> dict:
    with open("config.txt") as input_file:
        data = input_file.readlines()

    config = {}
    for line in data:
        line = line.split(":")
        config[line[0].strip()] = line[1].strip()
    return config


def main():
    config = load_config()
    sensor = init_ath()
    print("Sensor initialised")
    screen = init_screen()
    print("Screen initialised")
    screen.fill(screen.BLACK)
    wlan = wifi.StatefulWLAN(config["ssid"], config["password"])
    wlan.connect()
    print("Wifi initialised")
    loop(sensor, screen, wlan)


if __name__ == '__main__':
    main()
