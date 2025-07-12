from time import sleep

from ext.typing.typing import Optional
from ext.waveshare.lcd import LCD

import network
import image

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

    def check_status(self, screen: Optional[LCD] = None) -> int:
        """Check the status of the Wi-Fi connection."""
        status = self.status()
        print(f"Wifi status: {status}")
        if status != 3:
            self.disconnect()
            self.connect()
        if screen:
            self._update_wifi_icon(status, screen)
        self.previous_status = status
        return status

    def _update_wifi_icon(self, status: int, screen: LCD):
        screen.blit(self.wifi_image.get_framebuffer(), 120, 2)
        if status != 3:
            screen.blit(self.x_image.get_framebuffer(), 120, 1, 0)
        screen.show()

    def initialise(self, screen: LCD) -> bool:
        """Initialise the Wi-Fi connection. Return True on success."""
        self.connect()
        i = 0
        while i < 10:
            screen.fill(screen.BLACK)
            screen.text(f"Connecting... {i}", 5, 5, screen.WHITE)
            screen.show()
            sleep(1)
            status = self.check_status()
            if status == 3:
                screen.fill(screen.BLACK)
                screen.text(f"IP: {self.ifconfig()[0]}", 5, 5, screen.WHITE)
                screen.show()
                sleep(1)
                print("Wifi connected")
                return True
            i += 1

        screen.fill(screen.BLACK)
        screen.text(f"Unable to connect to wifi", 5, 5, screen.WHITE)
        print("Unable to connect to Wifi")
        screen.show()
        sleep(1)
        screen.fill(screen.BLACK)
        return False
