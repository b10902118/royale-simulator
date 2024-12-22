from PIL import Image, ImageDraw
import json
import glob
import random
from os import path, makedirs
import numpy as np
from tqdm import tqdm

backgrounds = [Image.open(p) for p in glob.glob("cropped_bg/*.png")]

base_dirs = [
    "giant",
    "musketeer",
    "mini_pekka",
    "minion",
    "goblin",
]

cls_num = {name: i for i, name in enumerate(base_dirs)}

image_paths = []
for base_dir in base_dirs:
    image_paths += glob.glob(path.join(base_dir, "*.png"))


output_dir = "data/"
images_dir = path.join(output_dir, "images")
labels_dir = path.join(output_dir, "labels")
if not path.exists(images_dir):
    makedirs(images_dir)

if not path.exists(labels_dir):
    makedirs(labels_dir)


def get_random_position(background_size, image_size):
    bg_width, bg_height = background_size
    img_width, img_height = image_size
    x = random.randint(0, bg_width - img_width)
    y = random.randint(0, bg_height - img_height)
    return x, y


# LEVEL_WIDTH = 10
# LEVEL_HEIGHT = 16
# HP_BAR_HEIGHT = 6

level_images = {
    "blue": Image.open("./props/level_blue.png"),
    "red": Image.open("./props/level_red.png"),
}
LEVEL_W = 28
LEVEL_H = 34

health_images = {
    "blue": Image.open("./props/health_blue.png"),
    "red": Image.open("./props/health_red.png"),
}
HP_H = 16
HP_OFF_H = LEVEL_H // 2 - HP_H // 2

for color in ["blue", "red"]:
    health_images[color] = health_images[color].resize(
        (health_images[color].width, HP_H)
    )
    level_images[color] = level_images[color].resize((LEVEL_W, LEVEL_H))

ELIXER_COLOR = (174, 86, 234)

clock_image = Image.open("./props/clock.png")


def draw_health_bar(pos, chr_img, background):
    x, y = pos
    color = random.choice(["blue", "red"])
    level_only = random.choice([True, False])

    if level_only and color != "blue":
        x_off = chr_img.width // 2 - LEVEL_W // 2
        y_off = random.randint(-40, 0)
        background.paste(
            level_images[color], (x + x_off, y + y_off), level_images[color]
        )

    else:
        x_off = random.randint(-20, 0)
        y_off = random.randint(-40, 0)
        hbar = health_images[color].copy()
        hbar_width = random.randint(5, round(chr_img.width))
        hbar = hbar.resize((hbar_width, hbar.height))

        level_x = x + x_off
        level_y = y + y_off
        background.paste(level_images[color], (level_x, level_y), level_images[color])
        background.paste(hbar, (level_x + LEVEL_W, level_y + HP_OFF_H), hbar)


def draw_clock(pos, chr_img, background):
    x, y = pos
    x_off = chr_img.width // 2 - clock_image.width // 2
    if clock_image.height > chr_img.height:
        y_off = chr_img.height + random.randint(
            -chr_img.height // 3, clock_image.height
        )
    else:
        y_off = chr_img.height + random.randint(
            -clock_image.height, clock_image.height // 2
        )
    background.paste(clock_image, (x + x_off, y + y_off), clock_image)


# Image.open(image_paths[0])
# draw_health_bar(Image.open(image_paths[0])).show()

# exit()


def draw_elixers(scene):
    # Draw irregular shape with color similar to ELIXER_COLOR
    shape = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    shape_draw = ImageDraw.Draw(shape)
    num_ovals = random.randint(5, 10)
    for _ in range(num_ovals):
        x0 = random.randint(0, scene.width)
        y0 = random.randint(0, scene.height)
        x1 = x0 + random.randint(20, 100)
        y1 = y0 + random.randint(20, 100)
        color_variation = (
            ELIXER_COLOR[0] + random.randint(-20, 20),
            ELIXER_COLOR[1] + random.randint(-20, 20),
            ELIXER_COLOR[2] + random.randint(-20, 20),
            random.randint(128, 256),  # Alpha value for transparency
        )
        shape_draw.ellipse([x0, y0, x1, y1], fill=color_variation)
    scene = Image.alpha_composite(scene.convert("RGBA"), shape)
    return scene


def draw_chr_effect(chr_img):
    color = random.choice(["blue", "red"])
    overlay = Image.new("RGBA", chr_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    chr_array = np.array(chr_img)
    alpha_channel = chr_array[:, :, 3]
    mask = alpha_channel > 20

    overlay_array = np.zeros_like(chr_array)

    black = random.randint(0, 128)
    alpha = random.randint(64, 196)
    filter_color = (
        [black, black, 255, alpha] if color == "blue" else [255, black, black, alpha]
    )
    overlay_array[mask] = filter_color

    overlay = Image.fromarray(overlay_array)
    chr_img = Image.alpha_composite(chr_img.convert("RGBA"), overlay)
    return chr_img


# annotations = {}
for i in tqdm(range(3000)):  # Generate 10 synthetic images
    bg = random.choice(backgrounds).copy()

    positions_images = []
    n = random.randint(8, 20)
    for _ in range(n):  # random.randint(1, 5)):  # Random number of images to paste
        img_path = random.choice(image_paths)
        img = Image.open(img_path)
        position = get_random_position(bg.size, img.size)
        cls_name = img_path.split("/")[-2]
        positions_images.append(
            (
                position,
                img,
                cls_num[cls_name],
            )
        )

    # Sort images based on their bottom y coordinate (small y to big y)
    positions_images.sort(key=lambda x: x[0][1] + x[1].size[1])

    bbox = []
    for position, img, clsn in positions_images:
        if random.random() < 0.3:
            img = draw_chr_effect(img)
        bg.paste(img, position, img)
        if random.random() < 0.8:
            draw_health_bar(position, img, bg)
        if random.random() < 0.2:
            draw_clock(position, img, bg)
        img_width, img_height = img.size
        x_center = position[0] + img_width / 2
        y_center = position[1] + img_height / 2
        bbox.append(
            (
                clsn,
                x_center / bg.width,
                y_center / bg.height,
                img_width / bg.width,
                img_height / bg.height,
            )
        )

    # Add shadow to the image
    if random.random() < 0.3:
        shadow = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_radius = random.randint(bg.width // 4, bg.width // 3)
        shadow_x = random.randint(0, bg.width)
        shadow_y = random.randint(0, bg.height)
        shadow_draw.ellipse(
            (
                shadow_x - shadow_radius,
                shadow_y - shadow_radius,
                shadow_x + shadow_radius,
                shadow_y + shadow_radius,
            ),
            fill=(0, 0, 0, 50),
        )
        bg = Image.alpha_composite(bg.convert("RGBA"), shadow)

    if random.random() < 0.5:
        bg = draw_elixers(bg)

    # Draw bounding boxes on the image
    # draw = ImageDraw.Draw(bg)
    # assert len(bbox) == n
    # for box in bbox:
    #    clsn, x_center, y_center, width, height = box
    #    x0 = int((x_center - width / 2) * bg.width)
    #    y0 = int((y_center - height / 2) * bg.height)
    #    x1 = int((x_center + width / 2) * bg.width)
    #    y1 = int((y_center + height / 2) * bg.height)
    #    draw.rectangle([x0, y0, x1, y1], outline="red", width=2)
    #    draw.text((x0, y0), str(clsn), fill="red")

    # Draw bounding boxes on the image
    # draw = ImageDraw.Draw(bg)
    # for box in bbox:
    #     width = round(box[3] * bg.width)
    #     height = round(box[4] * bg.height)
    #     x0 = round(box[1] * bg.width - width / 2)
    #     y0 = round(box[2] * bg.height - height / 2)
    #     draw.rectangle(
    #         [x0, y0, x0 + width, y0 + height],
    #         outline="red",
    #         width=2,
    #     )

    bg.save(path.join(images_dir, f"{i}.png"))
    with open(path.join(labels_dir, f"{i}.txt"), "w") as f:
        for box in bbox:
            f.write(" ".join(map(str, box)) + "\n")

# with open(f"annotations.json", "w") as f:
#    json.dump(annotations, f, indent=4)


# centers = []
# for base_dir in base_dirs:
#    with open(base_dir + "centers.json", "r") as f:
#        centers += json.load(f)
