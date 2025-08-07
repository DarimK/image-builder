import cv2
import numpy as np

# Resizes an image to the given dimensions
def resizeImage(image, width, height = 0):
    if height == 0:
        height = int(width / image.shape[1] * image.shape[0])

    # Resizes with INTER_AREA if shrinking, otherwise with INTER_CUBIC
    if (width * height) / (image.shape[1] * image.shape[0]) < 1:
        return cv2.resize(image, (width, height), cv2.INTER_AREA).astype(np.uint8)
    else:
        return cv2.resize(image, (width, height), cv2.INTER_CUBIC).astype(np.uint8)

# Converts an image from RGB to RGBA format
def convertToRGBA(image):
    # Appends an alpha value of 255 to every pixel if in RGB format
    if image.shape[2] == 3:
        alpha = np.full((image.shape[0], image.shape[1], 1), 255)
        image = np.concatenate((image, alpha), axis=2)

    # Force converts alpha value to int (if float)
    image[image[:, :, 3] == 0] = 0
    return image.astype(np.uint8)

# Finds an image from a list of images that best matches the given image block
def bestImage(imageBlock, imageList, avgList):
    # Gets the average color of the block
    avgColor = np.nanmean(imageBlock, axis=(0, 1))

    # If the image block is mostly transparent, return a transparent block, otherwise the best matching
    if avgColor[3] < 128:
        return np.zeros((imageBlock.shape[1], imageBlock.shape[0], 4), dtype=np.uint8)
    else:
        best = None
        bestDist = float('inf')
        
        # Finds the Euclidean distance between the average color and every image, selects the lowest
        for i in range(len(imageList)):
            distance = np.linalg.norm(avgColor - avgList[i])
            if distance < bestDist:
                best = imageList[i]
                bestDist = distance
        return best.astype(np.uint8)

# Builds a mosaic replica of the base image from the image list
def build(baseImage, imageList, size, basePresence):
    # Formats the base image and stores its width and height
    width, height = baseImage.shape[1], baseImage.shape[0]
    baseImage = convertToRGBA(resizeImage(baseImage, width - width % size, height - height % size))
    width, height = baseImage.shape[1], baseImage.shape[0]

    # Formats every image in the list to the requested size and stores their average colors
    imageList = [convertToRGBA(resizeImage(image, size, size)) for image in imageList]
    avgList = [np.nanmean(image, axis=(0, 1)) for image in imageList]

    # Creates a blank image which will be built upon
    img = np.zeros((height, width, 4), dtype=np.uint8)

    # Finds the best match for every block of the base image and adds it to the blank image
    for x in range(0, width, size):
        for y in range(0, height, size):
            best = bestImage(baseImage[y: y + size, x: x + size], imageList, avgList)
            
            # Places the best match on the blank image, including the requested base color presence
            img[y: y + size, x: x + size] = cv2.addWeighted(best, 1 - basePresence, baseImage[y: y + size, x: x + size], basePresence, 0)
            
    return img