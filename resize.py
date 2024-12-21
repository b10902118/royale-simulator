import os
import argparse
from PIL import Image
from shutil import copyfile

scales = {
    "goblin": 1.1329,
    "basic_cannon": 2.7308,
    "giant": 1.6652,
    "minion": 0.9466,
    "musketeer": 1.2943,
    "mini_pekka": 1.08,
}


def get_folder(card_name):
    if card_name == "basic_cannon":
        return "building_basic_cannon_out"
    else:
        return f"chr_{card_name}_out"


def resize_images_in_folder(folder_path, card_name, scale):
    os.makedirs(card_name, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            image_src = os.path.join(folder_path, filename)
            image_dst = os.path.join(card_name, filename)
            with Image.open(image_src) as img:
                new_size = (int(img.width * scale), int(img.height * scale))
                resized_img = img.resize(new_size, Image.LANCZOS)
                resized_img.save(image_dst)
                # print(f"Resized {filename} to {new_size}")
        else:  # centers
            copyfile(
                os.path.join(folder_path, filename), os.path.join(card_name, filename)
            )


for card_name, scale in scales.items():
    folder = get_folder(card_name)
    resize_images_in_folder(folder, card_name, scale)


# if __name__ == "__main__":
#    parser = argparse.ArgumentParser(description="Resize images in a folder.")
#    parser.add_argument(
#        "folder", type=str, help="Path to the folder containing images."
#    )
#    parser.add_argument("scale", type=float, help="Scale factor for resizing images.")
#
#    args = parser.parse_args()
#
#    resize_images_in_folder(args.folder, args.scale)
