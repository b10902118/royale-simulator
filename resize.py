import os
import argparse
from PIL import Image


def resize_images_in_folder(folder_path, scale=0.56):
    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            image_path = os.path.join(folder_path, filename)
            with Image.open(image_path) as img:
                new_size = (int(img.width * scale), int(img.height * scale))
                resized_img = img.resize(new_size, Image.LANCZOS)
                resized_img.save(image_path)
                print(f"Resized {filename} to {new_size}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resize images in a folder.")
    parser.add_argument(
        "folder", type=str, help="Path to the folder containing images."
    )
    parser.add_argument("scale", type=float, help="Scale factor for resizing images.")

    args = parser.parse_args()

    resize_images_in_folder(args.folder, args.scale)
