from PIL import Image
import matplotlib.pyplot as plt


def process_image(input_path, output_path):
    # Open the input image
    img = Image.open(input_path).convert("RGBA")
    pixels = img.load()

    # Create a new image with RGB mode
    new_img = Image.new("RGB", img.size)
    new_pixels = new_img.load()

    # Initialize alpha distribution list
    alpha_distribution = [0] * 256

    # Process each pixel
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b, a = pixels[x, y]
            alpha_distribution[a] += 1
            if a <= 200:
                new_pixels[x, y] = (0, 0, 0)  # Black
            else:
                new_pixels[x, y] = (255, 255, 255)  # White

    # Save the new image
    new_img.save(output_path)

    # Plot the alpha distribution
    plt.plot(alpha_distribution)
    plt.title("Alpha Distribution")
    plt.xlabel("Alpha Value")
    plt.ylabel("Frequency")
    plt.show()


# Example usage
process_image("chr_mini_pekka_out/chr_mini_pekka_sprite_415.png", "mini_map200.png")
