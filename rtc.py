import machine
import urequests as requests

class Clock:
    def __init__(self):
        self.clock = machine.RTC()


    def time(self):
        return self.clock.datetime()

    def initialise(self):
        r = requests.get("https://www.google.com")
        print(r.content)