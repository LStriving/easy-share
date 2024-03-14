def debug_base64_image(base64_image, filename):
    with open(filename, "w") as file:
        file.write(base64_image)