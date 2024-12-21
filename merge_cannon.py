from PIL import Image


def stack_images_center(image1_path, image2_path, output_path):
    # Open the images
    img1 = Image.open(image1_path)
    img2 = Image.open(image2_path)

    # Get the dimensions of the images
    w1, h1 = img1.size
    w2, h2 = img2.size

    # Calculate the center offsets
    y_offset = (h2 - h1) // 2
    x_offset = (w2 - w1) // 2

    # Create a new image with the size of the second image
    stacked_image = Image.new("RGB", (w2, h2))

    # Place the second image on the new image
    stacked_image.paste(img2, (0, 0))

    # Place the first image on the new image, centered
    stacked_image.paste(img1, (x_offset, y_offset), img1)

    # Save the result
    stacked_image.save(output_path)


# Example usage
stack_images_center("/path/to/image1.jpg", "/path/to/image2.jpg", "/path/to/output.jpg")
