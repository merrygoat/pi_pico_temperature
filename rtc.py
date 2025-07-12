import machine
import socket
import struct
import time

class Clock:
    def __init__(self):
        self.clock = machine.RTC()

    @staticmethod
    def time(seconds: bool = True) -> str:
        """Returns a string representing the current time in UTC."""
        t = time.localtime()
        if seconds:
            return f"{t[3]:02}:{t[4]:02}:{t[5]:02}"
        else:
            return f"{t[3]:02}:{t[4]:02}"

    @staticmethod
    def date():
        t = time.localtime()
        return f"{t[2]:02}-{t[1]:02}-{t[0]}"

    @staticmethod
    def datetime():
        t = time.localtime()
        return f"{t[3]:02}:{t[4]:02}:{t[5]:02} {t[2]:02}/{t[1]:02}/{t[0]}"


    def initialise(self):
        """Get the time from an NTP server and use this to set the clock."""
        ntp_request = bytearray(48)
        ntp_request[0] = 0x23
        addr = socket.getaddrinfo("pool.ntp.org", 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.settimeout(1)
            s.sendto(ntp_request, addr)
            msg = s.recv(48)
        finally:
            s.close()
        # Bytes 40-44 are the 32 bits representing the seconds part of the NTP server TX time
        val = struct.unpack("!I", msg[40:44])[0]
        # Subtract the epoch time
        t = val - 2208988800
        tm = time.gmtime(t)
        self.clock.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
        print(f"Set time to: {self.datetime()}")