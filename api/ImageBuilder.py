import cv2
import numpy as np

# Resizes an image to the given dimensions
def resize_image(image, width, height = 0):
    if height == 0:
        height = int(width / image.shape[1] * image.shape[0])

    # Resizes with INTER_AREA if shrinking, otherwise with INTER_CUBIC
    if (width * height) / (image.shape[1] * image.shape[0]) < 1:
        return cv2.resize(image, (width, height), cv2.INTER_AREA).astype(np.uint8)
    else:
        return cv2.resize(image, (width, height), cv2.INTER_CUBIC).astype(np.uint8)

# Converts an image from RGB to RGBA format
def convert_to_RGBA(image):
    # Appends an alpha value of 255 to every pixel if in RGB format
    if image.shape[2] == 3:
        alpha = np.full((image.shape[0], image.shape[1], 1), 255)
        image = np.concatenate((image, alpha), axis=2)

    # Force converts alpha value to int (if float)
    image[image[:, :, 3] == 0] = 0
    return image.astype(np.uint8)

# Finds an image from a list of images that best matches the given image block
def best_image(image_block, image_list, avg_list):
    # Gets the average color of the block
    avg_color = np.nanmean(image_block, axis=(0, 1))

    # If the image block is mostly transparent, return a transparent block, otherwise the best matching
    if avg_color[3] < 128:
        return np.zeros((image_block.shape[1], image_block.shape[0], 4), dtype=np.uint8)
    else:
        best = None
        best_dist = float('inf')
        
        # Finds the Euclidean distance between the average color and every image, selects the lowest
        for i in range(len(image_list)):
            distance = np.linalg.norm(avg_color - avg_list[i])
            if distance < best_dist:
                best = image_list[i]
                best_dist = distance
        return best.astype(np.uint8)

# Builds a mosaic replica of the base image from the image list
def build(base_image, image_list, size, base_presence):
    # Formats the base image and stores its width and height
    width, height = base_image.shape[1], base_image.shape[0]
    base_image = convert_to_RGBA(resize_image(base_image, width - width % size, height - height % size))
    width, height = base_image.shape[1], base_image.shape[0]

    # Formats every image in the list to the requested size and stores their average colors
    image_list = [convert_to_RGBA(resize_image(image, size, size)) for image in image_list]
    avg_list = [np.nanmean(image, axis=(0, 1)) for image in image_list]

    # Creates a blank image which will be built upon
    img = np.zeros((height, width, 4), dtype=np.uint8)

    # Finds the best match for every block of the base image and adds it to the blank image
    for x in range(0, width, size):
        for y in range(0, height, size):
            best = best_image(base_image[y: y + size, x: x + size], image_list, avg_list)
            
            # Places the best match on the blank image, including the requested base color presence
            img[y: y + size, x: x + size] = cv2.addWeighted(best, 1 - base_presence, base_image[y: y + size, x: x + size], base_presence, 0)
            
    return img