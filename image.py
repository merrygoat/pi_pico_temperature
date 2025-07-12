import deflate
import framebuf
from machine import PWM, Pin

from ext.waveshare.lcd import LCD, BL


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
        """Assumes data are compressed space delimited integers. First letter indicates image format, second
        indicates number of pixels per row, third indicates number of rows. Following integers are pixel values in row,
        column order."""
        with open(filename, 'rb') as f:
            with deflate.DeflateIO(f, deflate.ZLIB) as d:
                self.data = d.read()
        self.mode = self.data[0]
        if self.mode not in self.valid_modes:
            raise SyntaxError("Error reading image from '{filename}'. Invalid image mode.")
        self.width = int(self.data[1])
        self.height = int(self.data[2])
        self.data = [int(x) for x in self.data[3:]]
        if len(self.data) != self.width * self.height:
            raise SyntaxError("Error reading image from '{filename}'. Number of pixels does not match width and height.")

    def get_framebuffer(self) -> framebuf.FrameBuffer:
        if self.mode == 0:
            self._greyscale_to_colour()

        buffer = framebuf.FrameBuffer(bytearray(self.height * self.width * 2), self.width, self.height, framebuf.RGB565)
        for x in range(self.width):
            for y in range(self.height):
                buffer.pixel(x, y, self.data[x + y * self.width])
        return buffer

    def _greyscale_to_colour(self):
        """Convert an 8 bit greyscale image to little-endian RGB565."""
        self.data = [(pixel & 0b00011100) << 11 |  # low end of green
                     (pixel & 0b11111000) << 5 |   # blue
                     (pixel & 0b11111000) |        # red
                     (pixel & 0b11100000) >> 5     # High end of green
                     for pixel in self.data]
        self.mode = 1


def init_screen() -> LCD:
    """Initialise LCD object."""
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)
    screen = LCD()
    screen.fill(screen.BLACK)
    screen.show()
    return screen
