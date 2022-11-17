from PIL import Image
import PIL.ImageOps
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

x = 64
y = 64
colour = 0    # 0 for greyscale 1 for BRG556
invert = True


def main(input_path: str, output_path: str):
    matplotlib.use("TkAgg")

    with Image.open(input_path) as im:
        data = im.convert("L")
    data = PIL.ImageOps.invert(data)
    data = data.resize((64, 64), Image.Resampling.LANCZOS)
    data = np.array(data)

    plt.imshow(data, cmap="gray")
    plt.show()
    data = list(data.flatten())
    data = [colour, x, y] + data
    with open(output_path, "wb") as output_file:
        output_file.write(bytes(data))


if __name__ == "__main__":
    main("C:/Users/Peter/Desktop/wifi.png", "output.bin")