import os
from PIL import Image

# Set the folder path
folder_path = "./"
output_folder = "./cropped"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

i = 0
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".png"):
        image_path = os.path.join(folder_path, filename)
        with Image.open(image_path) as img:
            width, height = img.size

            # Define cropping box: (left, upper, right, lower)
            left, upper, right, lower = 0, 120, width, min(height, 1850)
            cropped_image = img.crop((left, upper, right, lower))

            # Save cropped image
            output_path = os.path.join(output_folder, f"{i}.png")
            cropped_image.save(output_path)
        i += 1

print("Images cropped and saved in:", output_folder)
