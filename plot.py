from ext.waveshare.lcd import LCD


class ScatterPlot:
    """A scatter plot."""

    def __init__(self, screen: LCD, origin: tuple[int, int], size: tuple[int, int], line_colour: int = 0xFFFF):
        """
        :param screen: An instance of the LCD screen class.
        :param origin: x and y coordinates of top left of plot bounding box in pixels.
        :param size: x and y size of plot bounding box in pixels.
        :param line_colour: Colour of plot lines in hex representation of RGB565.
        """
        self.screen = screen
        self.position = 0
        self.x, self.y = origin
        self.x_len, self.y_len = size
        self.colour = line_colour
        self.show_border = False

    def plot_border(self):
        self.screen.rect(self.x, self.y, self.x_len, self.y_len, self.colour)

    def plot_axis_labels(self, x_min: int, x_max: int):
        pass

    def plot_axis(self, left_pad: int = 20, right_pad: int = 5, bottom_pad: int = 12,
                  top_pad: int = 5) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]:
        """Plot the graph axis leaving room for labels and ticks.
        :param left_pad: The distance between the left side of the bounding box and the y-axis
        :param right_pad: The distance between the right side of the bounding box and the right end of the x-axis
        :param bottom_pad: The distance between the bottom of the bounding box and the x-axis
        :param top_pad: The distance between the top side of the bounding box and the top end of the y-axis
        :return: Two tuples giving x0, y0, x1 and y1 for the x and y axes respectively.
        """
        origin = (self.x + left_pad, self.y + self.y_len - bottom_pad)
        x_axis = (origin[0], origin[1], origin[0] + self.x_len - left_pad - right_pad, origin[1])
        y_axis = (origin[0], self.y + top_pad, origin[0], origin[1])
        self.screen.line(x_axis[0], x_axis[1], x_axis[2], x_axis[3], self.colour)
        self.screen.line(y_axis[0], y_axis[1], y_axis[2], y_axis[3], self.colour)
        return x_axis, y_axis

    def plot_x_labels(self, x_labels: list[float], x_axis: tuple[int, int, int, int]):
        """Plot the ticks and labels on the x-axis. Assumes labels are evenly spaced."""
        tick_length = 4
        axis_length = x_axis[2] - x_axis[0]
        step = axis_length / (len(x_labels) - 1)
        for index, label in enumerate(x_labels):
            label = str(label)
            x_pos = int(index * step) + x_axis[0]
            y_pos = x_axis[1]
            # Print tick
            self.screen.vline(x_pos, y_pos, tick_length, self.colour)
            # Print label
            self.screen.text(label, x_pos - (4 * len(label)), y_pos + tick_length + 4, self.colour)

    def plot_y_labels(self, y_labels: list[float], y_axis: tuple[int, int, int, int]):
        """Plot the ticks and labels on the y-axis. Assumes labels are evenly spaced."""
        tick_length = 4
        axis_length = y_axis[3] - y_axis[1]
        step = axis_length / (len(y_labels) - 1)
        for index, label in enumerate(y_labels):
            label = str(label)
            x_pos = y_axis[0] - tick_length
            y_pos = y_axis[3] - int(index * step)
            # Print tick
            self.screen.hline(x_pos, y_pos, tick_length, self.colour)
            # Print label
            self.screen.text(label, x_pos - (8 * len(label)) - tick_length, y_pos - 4, self.colour)

    def update_plot(self, data: tuple[list[float], list[float]], x_range: tuple[int, int] = None,
                    y_range: tuple[int, int] = None, x_ticks: tuple[int, int] = None, y_ticks: tuple[int, int] = None):
        x_data, y_data = data
        self.screen.fill_rect(self.x, self.y, self.x_len, self.x_len, self.screen.BLACK)

        if self.show_border:
            self.plot_border()

        x_axis, y_axis = self.plot_axis()

        self.plot_x_labels([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], x_axis)
        self.plot_y_labels([1, 2, 3, 4, 5, 6], y_axis)

        self.screen.show()
