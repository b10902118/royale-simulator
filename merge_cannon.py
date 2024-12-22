from PIL import Image
from glob import glob
import json
import os
from os import path

output_dir = "./basic_cannon_merged"
os.makedirs(output_dir, exist_ok=True)

image_dir = "./building_basic_cannon_out"

centers = json.load(open(path.join(image_dir, "centers.json")))

base_image = Image.open(path.join(image_dir, "0.png"))
bx, by = centers["0"]

bl = round(bx * base_image.width)
br = round(base_image.width - bl)
bt = round(by * base_image.height)
bb = round(base_image.height - bt)

for key, center in centers.items():
    if key == "0":
        continue
    x, y = center
    tube_image = Image.open(path.join(image_dir, f"{key}.png"))
    l = round(x * tube_image.width)
    r = round(tube_image.width - l)
    t = round(y * tube_image.height)
    b = round(tube_image.height - t)

    w = max(bl, l) + max(br, r)
    h = max(bt, t) + max(bb, b)

    new_image = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    base_offset = [0, 0]
    tube_offset = [0, 0]

    if bl > l:
        base_offset[0] = 0
        tube_offset[0] = bl - l
    else:
        base_offset[0] = l - bl
        tube_offset[0] = 0

    if bt > t:
        base_offset[1] = 0
        tube_offset[1] = bt - t
    else:
        base_offset[1] = t - bt
        tube_offset[1] = 0

    new_image.paste(base_image, base_offset, base_image)
    new_image.paste(tube_image, tube_offset, tube_image)

    new_image.save(f"{output_dir}/{key}.png")
