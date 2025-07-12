from PIL import Image, ImageDraw, ImageFont
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("TkAgg")
font_size = 128

# make a blank image for the text, initialized to transparent text color
img = Image.new("RGBA", (font_size, font_size))

# get a font
fnt = ImageFont.truetype(r"C:\Users\Peter\Downloads\Roboto\Roboto-Regular.ttf", font_size)
# get a drawing context
d = ImageDraw.Draw(img)
d.fontmode = "L"
# draw text
d.text((0, 0), "A", font=fnt, fill=1)

data = np.asarray(img)
plt.imshow(data, interpolation='none')
plt.show()
