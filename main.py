from time import sleep
from machine import Pin, I2C, PWM

from ext.aht.aht20 import AHT20
from ext.waveshare.lcd import LCD, BL

import wifi
import progress
import rtc
import sensors


def loop(sensor: AHT20, screen: LCD, wlan: wifi.StatefulWLAN, clock: rtc.Clock):
    progress_icon = progress.ProgressIcon(screen, 145, 3)
    temperature = sensors.Temperature(10)
    humidity = sensors.Humidity(10)
    print("Loop initialised")
    print(clock.time())
    time = 0
    while True:
        print(f"Tick {time}")
        if time % 1 == 0:
            sample_sensor(sensor, temperature, humidity)
            update_screen(screen, temperature, humidity, progress_icon)
            # plot_graph(plot, temperature.history)
        if time % 10 == 0:
            status = wlan.check_status()
            wlan.update_wifi_icon(status, screen)
        time += 1
        if time == 10:
            time = 0
        sleep(1)


def sample_sensor(sensor: AHT20, temperature: sensors.Temperature, humidity: sensors.Humidity):
    temperature.update_value(round(sensor.temperature, 2))
    humidity.update_value(round(sensor.relative_humidity, 2))


def update_screen(screen: LCD, temperature: sensors.Temperature, humidity: sensors.Humidity, progress_icon: progress.ProgressIcon):
    temperature.print_to_screen(screen)
    humidity.print_to_screen(screen)
    progress_icon.tick(screen)
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
    clock = rtc.Clock()
    loop(sensor, screen, wlan, clock)


if __name__ == '__main__':
    main()
