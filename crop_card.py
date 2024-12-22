from PIL import Image


def crop_image(input_path, output_path, y_start, y_end):
    # Open an image file
    with Image.open(input_path) as img:
        # Define the cropping box (left, upper, right, lower)
        box = (245, 1930, 1180, 2200)
        # Crop the image
        cropped_img = img.crop(box)
        ch = cropped_img.height
        cw = cropped_img.width // 4
        card1 = cropped_img.crop((0, 0, cw, ch))
        card2 = cropped_img.crop((cw, 0, 2 * cw, ch))
        card3 = cropped_img.crop((2 * cw, 0, 3 * cw, ch))
        card4 = cropped_img.crop((3 * cw, 0, 4 * cw, ch))
        card4.show()
        # Save the cropped image
        # cropped_img.show()
        # cropped_img.save(output_path)


if __name__ == "__main__":
    input_image_path = "arena.png"
    output_image_path = "cropped_arena_whole.jpg"
    y_start = 280
    y_end = 1800

    crop_image(input_image_path, output_image_path, y_start, y_end)
