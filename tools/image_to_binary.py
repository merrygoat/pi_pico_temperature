from PIL import Image
import PIL.ImageOps
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import zlib
matplotlib.use("TkAgg")


def image_to_bin(input_path: str, output_path: str, dimensions: tuple, crop: tuple, invert=False, mode="RGB"):
    """Convert an image to a compressed binary format.

    :param input_path: The path to read the image.
    :param output_path: The path to store the compressed binary.
    :param dimensions: A 2 value tuple of x and y dimensions of the output image.
    :param crop: A 4 value tuple describing the top, bottom, left, and right crop values.
    :param invert: Whether to invert the colour of the image.
    :param mode: "L" for greyscale, "RGB" for RGB.
    """

    x, y = dimensions
    top_crop, bottom_crop, left_crop, right_crop = crop

    with Image.open(input_path) as im:
        data = im.convert(mode)
    if invert:
        data = PIL.ImageOps.invert(data)
    data = data.resize((x, y), Image.Resampling.BICUBIC)
    data = np.array(data)

    plot_cropped_image(data, mode, top_crop, bottom_crop, left_crop, right_crop)
    if mode == "L":
        data = list(data[top_crop:bottom_crop, left_crop:right_crop].flatten())
        data = [0, (right_crop - left_crop), (bottom_crop - top_crop)] + data
    else:
        data = data[top_crop:bottom_crop, left_crop:right_crop]
        data = data.reshape((data.shape[0] * data.shape[1], 3))
        data = [(pixel[1] & 0b00011100) << 11 |  # low end of green
                (pixel[2] & 0b11111000) << 5 |  # blue
                (pixel[0] & 0b11111000) |  # red
                (pixel[1] & 0b11100000) >> 5  # High end of green
                for pixel in data]
        data = [1, (right_crop - left_crop), (bottom_crop - top_crop)] + data

    data = zlib.compress(bytes(data))
    with open(output_path, "wb") as output_file:
        output_file.write(data)


def plot_cropped_image(data: np.array, mode: str, top_crop: int, bottom_crop: int, left_crop: int, right_crop: int):
    if mode == "L":
        plt.imshow(data, cmap="gray", interpolation=None)
    else:
        plt.imshow(data, interpolation=None)
    plt.plot([left_crop - 0.5, right_crop - 0.5], [top_crop - 0.5, top_crop - 0.5], color='r', linestyle='--',
             linewidth=2)  # top crop
    plt.plot([left_crop - 0.5, right_crop - 0.5], [bottom_crop - 0.5, bottom_crop - 0.5], color='r', linestyle='--',
             linewidth=2)  # bottom crop
    plt.plot([left_crop - 0.5, left_crop - 0.5], [top_crop - 0.5, bottom_crop - 0.5], color='r', linestyle='--',
             linewidth=2)  # left crop
    plt.plot([right_crop - 0.5, right_crop - 0.5], [top_crop - 0.5, bottom_crop - 0.5], color='r', linestyle='--',
             linewidth=2)  # right crop
    ax = plt.gca()
    ax.set_aspect('equal')
    plt.show()


def greyscale_test_image(input_path: str, output_path: str):
    # Create a greyscale test gradient from black (left) to white (right).
    height = 50
    width = 100
    data = np.array([int(i * 256 / width) for i in range(width)] * height).reshape(height, width)

    plt.pcolormesh(data, edgecolors='w', linewidth=0.5, cmap="gray", vmin=0, vmax=255)

    ax = plt.gca()
    ax.set_aspect('equal')
    ax.invert_yaxis()

    plt.show()
    data = list(data.flatten())
    data = [0, width, height] + data
    with open(output_path, "wb") as output_file:
        output_file.write(bytes(data))


if __name__ == "__main__":
    image_to_bin("C:/Users/Peter/Desktop/wifi.png", "images/wifi.bin", (16, 16), (1, 15, 0, 16), mode="L", invert=True)
    image_to_bin("C:/Users/Peter/Desktop/x.png", "images/x.bin", (16, 16), (0, 16, 0, 16), mode="RGB")
