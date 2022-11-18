import network


class StatefulWLAN(network.WLAN):
    def __init__(self, ssid: str, password: str):
        super().__init__(network.STA_IF)
        self.previous_status = None
        self.ssid = ssid
        self.password = password
        self.active(True)

    def connect(self, **kwargs):
        super().connect(self.ssid, self.password)
