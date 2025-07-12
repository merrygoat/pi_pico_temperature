import network
from ext.waveshare.lcd import LCD
import image

import urequests

class StatefulWLAN(network.WLAN):
    def __init__(self, ssid: str, password: str):
        super().__init__(network.STA_IF)
        self.previous_status = None
        self.ssid = ssid
        self.password = password
        self.active(True)

        self.wifi_image = image.Image("images/wifi.bin")
        self.x_image = image.Image("images/x.bin")


    def connect(self, **kwargs):
        super().connect(self.ssid, self.password)


    def check_status(self) -> int:
        """Check the status of the Wi-Fi connection and update an icon on the screen to show the status."""
        status = self.status()
        print(f"Wifi status: {status}")
        if status != 3:
            self.disconnect()
            self.connect()
        self.previous_status = status
        return status

    def update_wifi_icon(self, status: int, screen: LCD):
        if status != self.previous_status:
            if self.previous_status != 3:
                screen.blit(self.wifi_image.get_framebuffer(), 120, 2)
            if status != 3:
                screen.blit(self.x_image.get_framebuffer(), 120, 1, 0)
            screen.show()
    #
    # def get_http(self, url: str):
    #     r = urequests.get("http://www.google.com")
    #     print(r.content)