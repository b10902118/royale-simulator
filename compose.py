from PIL import Image, ImageDraw
import json
import glob
import random
from os import path, makedirs

background = Image.open("arena_main.png")

base_dirs = [
    "giant/",
    "musketeer/",
    "mini_pekka/",
]

cls_num = {"giant": 0, "musketeer": 1, "mini_pekka": 2}

image_paths = []
for base_dir in base_dirs:
    image_paths += glob.glob(base_dir + "*.png")


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


# annotations = {}
for i in range(50):  # Generate 10 synthetic images
    new_image = background.copy()

    positions_images = []
    for _ in range(
        random.randint(3, 10)
    ):  # random.randint(1, 5)):  # Random number of images to paste
        img_path = random.choice(image_paths)
        img = Image.open(img_path)
        position = get_random_position(new_image.size, img.size)
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
        new_image.paste(img, position, img)
        img_width, img_height = img.size
        x_center = position[0] + img_width / 2
        y_center = position[1] + img_height / 2
        bbox.append(
            (
                clsn,
                x_center / new_image.width,
                y_center / new_image.height,
                img_width / new_image.width,
                img_height / new_image.height,
            )
        )

    # Add shadow to the image
    if random.random() < 0.3:
        shadow = Image.new("RGBA", new_image.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_radius = random.randint(new_image.height // 3, new_image.height // 2)
        shadow_x = random.randint(0, new_image.width)
        shadow_y = random.randint(0, new_image.height)
        shadow_draw.ellipse(
            (
                shadow_x - shadow_radius,
                shadow_y - shadow_radius,
                shadow_x + shadow_radius,
                shadow_y + shadow_radius,
            ),
            fill=(0, 0, 0, 50),
        )
        new_image = Image.alpha_composite(new_image.convert("RGBA"), shadow)

    # Draw bounding boxes on the image
    # draw = ImageDraw.Draw(new_image)
    # for box in bbox:
    #    clsn, x_center, y_center, width, height = box
    #    x0 = int((x_center - width / 2) * new_image.width)
    #    y0 = int((y_center - height / 2) * new_image.height)
    #    x1 = int((x_center + width / 2) * new_image.width)
    #    y1 = int((y_center + height / 2) * new_image.height)
    #    draw.rectangle([x0, y0, x1, y1], outline="red", width=2)
    #    draw.text((x0, y0), str(clsn), fill="red")

    # Draw bounding boxes on the image
    # draw = ImageDraw.Draw(new_image)
    # for box in bbox:
    #    draw.rectangle(box["bbox"], outline="red", width=2)

    new_image.save(path.join(images_dir, f"{i}.png"))
    with open(path.join(labels_dir, f"{i}.txt"), "w") as f:
        for box in bbox:
            f.write(" ".join(map(str, box)) + "\n")

# with open(f"annotations.json", "w") as f:
#    json.dump(annotations, f, indent=4)


# centers = []
# for base_dir in base_dirs:
#    with open(base_dir + "centers.json", "r") as f:
#        centers += json.load(f)
