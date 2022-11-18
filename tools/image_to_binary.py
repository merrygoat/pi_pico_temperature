from PIL import Image
import PIL.ImageOps
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")

x = 60
y = 40
top_crop = 0
bottom_crop = 50
left_crop = 0
right_crop = 100

colour = 0    # 0 for greyscale 1 for BRG556
invert = True


def greyscale_to_bin(input_path: str, output_path: str):
    matplotlib.use("TkAgg")

    with Image.open(input_path) as im:
        data = im.convert("L")
    data = PIL.ImageOps.invert(data)
    data = data.resize((x, y), Image.Resampling.BICUBIC)
    data = np.array(data)

    plt.pcolormesh(data, edgecolors='w', linewidth=0.5, cmap="gray")
    plt.plot([left_crop, right_crop], [top_crop, top_crop], color='r', linestyle='--', linewidth=2)  # top crop
    plt.plot([left_crop, right_crop], [bottom_crop, bottom_crop], color='r', linestyle='--', linewidth=2)  # bottom crop
    plt.plot([left_crop, left_crop], [top_crop, bottom_crop], color='r', linestyle='--', linewidth=2)  # left crop
    plt.plot([right_crop, right_crop], [top_crop, bottom_crop], color='r', linestyle='--', linewidth=2)  # right crop

    ax = plt.gca()
    ax.set_aspect('equal')
    ax.invert_yaxis()

    plt.show()
    data = list(data[top_crop:bottom_crop, left_crop:right_crop].flatten())
    data = [colour, (right_crop - left_crop), (bottom_crop - top_crop)] + data
    with open(output_path, "wb") as output_file:
        output_file.write(bytes(data))


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
    greyscale_test_image("C:/Users/Peter/Desktop/test.png", "images/output.bin")