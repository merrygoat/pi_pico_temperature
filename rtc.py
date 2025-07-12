import machine


class Clock:
    def __init__(self):
        self.clock = machine.RTC()


    def time(self):
        return self.clock.datetime()