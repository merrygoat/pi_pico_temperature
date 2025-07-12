from time import sleep

from ext.aht.aht20 import AHT20
from ext.waveshare.lcd import LCD

import wifi
import progress
import rtc
import sensors
from image import init_screen
from sensors import sample_sensor, init_ath


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
            wlan.check_status(screen)
        time += 1
        if time == 10:
            time = 0
        sleep(1)


def update_screen(screen: LCD, temperature: sensors.Temperature, humidity: sensors.Humidity, progress_icon: progress.ProgressIcon):
    temperature.print_to_screen(screen)
    humidity.print_to_screen(screen)
    progress_icon.tick(screen)
    screen.show()


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
    screen = init_screen()
    print("Screen initialised")
    sensor = init_ath()
    print("Sensor initialised")
    wlan = wifi.StatefulWLAN(config["ssid"], config["password"])
    connection_success = wlan.initialise(screen)
    clock = rtc.Clock()
    if connection_success:
        clock.initialise()
    loop(sensor, screen, wlan, clock)


if __name__ == '__main__':
    main()
