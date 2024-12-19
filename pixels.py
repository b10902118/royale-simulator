from PIL import Image


def load_and_print_pixels(image_path):
    with Image.open(image_path) as img:
        pixels = list(img.getdata())
        alpha_counts = {i: 0 for i in range(256)}

        blank_pixels = 0
        for pixel in pixels:
            if len(pixel) == 4:  # Check if the pixel has an alpha channel
                alpha = pixel[3]
                alpha_counts[alpha] += 1
                if alpha == 0:
                    if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
                        blank_pixels += 1

        print(f"Blank pixels: {blank_pixels}")
        for alpha, count in alpha_counts.items():
            print(f"Alpha {alpha}: {count} pixels")
            break
        print(f"Total pixels: {len(pixels)}")


# Example usage
image_path = "input.png"
black_path = "output2.png"
white_path = "output.png"
orig = Image.open(image_path)
black = Image.open(black_path)
white = Image.open(white_path)


def compare_images(image1, image2, image3):
    pixels1 = list(image1.getdata())
    pixels2 = list(image2.getdata())
    pixels3 = list(image3.getdata())

    differences = 0
    for p1, p2, p3 in zip(pixels1, pixels2, pixels3):
        if p1[:3] != p2[:3] or p1[:3] != p3[:3]:  # Compare only RGB values
            print(f"orig: {p1[:3]} black: {p2[:3]} white: {p3[:3]}")
            differences += 1

    print(f"Number of different pixels: {differences}")


compare_images(orig, black, white)

# load_and_print_pixels(image_path)
