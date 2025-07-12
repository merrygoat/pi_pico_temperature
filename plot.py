from math import log10

import collections

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

    def plot_x_labels(self, x_labels: list[str], x_axis: tuple[int, int, int, int]):
        """Plot the ticks and labels on the x-axis. Assumes labels are evenly spaced."""
        tick_length = 4
        axis_length = x_axis[2] - x_axis[0]
        step = axis_length / (len(x_labels) - 1)
        for index, label in enumerate(x_labels):
            x_pos = int(index * step) + x_axis[0]
            y_pos = x_axis[1]
            # Print tick
            self.screen.vline(x_pos, y_pos, tick_length, self.colour)
            # Print label
            self.screen.text(label, x_pos - (4 * len(label)), y_pos + tick_length + 4, self.colour)

    def plot_y_labels(self, y_labels: list[str], y_axis: tuple[int, int, int, int]):
        """Plot the ticks and labels on the y-axis. Assumes labels are evenly spaced."""
        tick_length = 4
        axis_length = y_axis[3] - y_axis[1]
        step = axis_length / (len(y_labels) - 1)
        for index, label in enumerate(y_labels):
            x_pos = y_axis[0] - tick_length
            y_pos = y_axis[3] - int(index * step)
            # Print tick
            self.screen.hline(x_pos, y_pos, tick_length, self.colour)
            # Print label
            self.screen.text(label, x_pos - (8 * len(label)) - tick_length, y_pos - 4, self.colour)

    def update_plot(self, data: tuple[list[float], list[float]], x_range: tuple[int, int] = None,
                    y_range: tuple[int, int] = None, x_ticks: tuple[int, int] = None, y_ticks: tuple[int, int] = None):
        x_data, y_data = data
        self.screen.fill_rect(0, self.y, 160, 128, self.screen.BLACK)
        if self.show_border:
            self.plot_border()

        x_axis, y_axis = self.plot_axis()

        x_labels = self.get_plot_labels(x_data, 8)
        y_labels = self.get_plot_labels(y_data, 6)

        self.plot_x_labels(x_labels, x_axis)
        self.plot_y_labels(y_labels, y_axis)

        self.plot_data_points(data, x_labels, y_labels, x_axis, y_axis)

        self.screen.show()

    def plot_data_points(self, data: tuple[list[float], list[float]], x_labels: list[str], y_labels: list[str],
                         x_axis: tuple[int, int, int, int], y_axis: tuple[int, int, int, int]):
        x_axis_min = float(x_labels[0])
        x_axis_max = float(x_labels[-1])
        print(f"x axis range: {x_axis_min}, {x_axis_max}")
        x_axis_range = x_axis_max - x_axis_min
        y_axis_min = float(y_labels[0])
        y_axis_max = float(y_labels[-1])
        print(f"y axis range: {y_axis_min}, {y_axis_max}")
        y_axis_range = y_axis_max - y_axis_min
        x_axis_pixel_min = x_axis[0]
        x_axis_pixel_max = x_axis[2]
        print(f"x axis pixel range: {x_axis_pixel_min}, {x_axis_pixel_max}")
        x_axis_pixel_range = x_axis_pixel_max - x_axis_pixel_min
        y_axis_pixel_min = y_axis[1]
        y_axis_pixel_max = y_axis[3]
        print(f"y axis pixel range: {y_axis_pixel_min}, {y_axis_pixel_max}")
        y_axis_pixel_range = y_axis_pixel_max - y_axis_pixel_min
        for index in range(len(data[0])):
            print(f"data: x {data[0][index]}, y{data[1][index]}")
            data_x_fraction = (data[0][index] - x_axis_min) / x_axis_range
            print(f"data: x fraction {data_x_fraction}")
            x_pixel_position = round(x_axis_pixel_min + (x_axis_pixel_range * data_x_fraction))
            print(f"data: x pixel position {x_pixel_position}")
            data_y_fraction = (data[1][index] - y_axis_min) / y_axis_range
            print(f"data: y fraction {data_y_fraction}")
            y_pixel_position = round(y_axis_pixel_max - (y_axis_pixel_range * data_y_fraction))
            print(f"data: y pixel position {y_pixel_position}")
            self.screen.pixel(x_pixel_position, y_pixel_position, self.colour)

    @staticmethod
    def get_plot_labels(axis_data: list[float], num_axis_points: int) -> list[str]:
        """Generate reasonable axis labels by considering the range of the data and rounding to nice numbers."""
        step = (max(axis_data) - min(axis_data)) / num_axis_points
        print(f"step: {step}")
        if step != 0:
            # round to 1 sig fig
            rounded_step = round(step, -int(log10(abs(step))))
            if rounded_step == 0:
                rounded_step = 1
        else:
            rounded_step = 1
        print(f"rounded step: {rounded_step}")
        labels = [(int(min(axis_data) / rounded_step) * rounded_step + (i * rounded_step)) for i in range(num_axis_points)]
                
        print(f"axis labels: {labels}")
        labels = [str(label) for label in labels]
        
        # Round labels to a sig fig which captures the range
        #label_sig_fig = round(log10(max(labels) - min(labels)))
        

        return labels


def plot_graph(plot: ScatterPlot, data: collections.deque):
    x_data = list(range(0, len(data)))
    y_data = list(data)
    data = (x_data, y_data)
    print(data)
    plot.update_plot(data)
