from PIL import Image
import glob
import random

# Calculates difference between two colors
def distance (color1, color2):
    if color1[3] == 0 and color2[3] == 0:
        return 0
    return (color2[0] - color1[0])**2 + (color2[1] - color1[1])**2 + (color2[2] - color1[2])**2 + (color2[3] - color1[3])**2

# Shrinks an image to be at most 1/20 of the base image
def sizeFix (img1, img2):
    baseWidth, baseHeight = img1.size
    imgWidth, imgHeight = img2.size
    sizeFactor = 20
    
    if imgWidth * sizeFactor < baseWidth and imgHeight * sizeFactor < baseHeight:
        return img2
    if imgWidth >= imgHeight:
        return img2.resize((int(baseWidth / sizeFactor), int(imgHeight / imgWidth * baseWidth / sizeFactor)))
    return img2.resize((int(imgWidth / imgHeight * baseHeight / sizeFactor), int(baseHeight / sizeFactor)))

# Returns a random position on the image, excluding transparent areas
def findPlacement (img):
    base = img.load()
    width, height = img.size

    while True:
        pos = (random.randrange(0, width), random.randrange(0, height))
        if base[pos[0], pos[1]][3]:
            return pos

# Takes in two images and a position, returns the color difference
def imageCompare (img1, img2, pos):
    base = img1.load()
    baseWidth, baseHeight = img1.size
    img = img2.load()
    imgWidth, imgHeight = img2.size
    total = 0
    count = 0

    for y in range(imgHeight):
        for x in range(imgWidth):
            total += distance(base[(x+pos[0]) % baseWidth, (y+pos[1]) % baseHeight], img[x, y])
            count += 1

    return total / count

# Takes in two images and a position, places the second image on the first at the position
def placeImage (img1, img2, pos):
    build = img1.load()
    buildWidth, buildHeight = img1.size
    img = img2.load()
    imgWidth, imgHeight = img2.size

    for y in range(imgHeight):
        for x in range(imgWidth):
            if img[x, y][3] > 0:
                build[(x+pos[0]) % buildWidth, (y+pos[1]) % buildHeight] = img[x, y]


if __name__ == "__main__":
    # Read in base image
    base = None
    print("Enter the base image name: ", end = "")

    while True:
        try:
            baseName = input()
            if len(baseName) == 0:
                raise OSError
            base = Image.open(baseName).convert("RGBA")
            break
        except OSError:
            print("Cannot find file or file is not an image. Please try again: ", end = "")

    # Create blank new image with same dimensions as base
    img = Image.new("RGBA", base.size, color=(0, 0, 0, 0))
    
    # Read in images from folder into image list
    imageList = []
    print("Enter the images folder name: ", end = "")

    while True:
        dirName = input()
        if len(dirName) and dirName[-1] != "\\":
            dirName += "\\"

        for name in (glob.glob(dirName + "*.png") + glob.glob(dirName + "*.jpg") + glob.glob(dirName + "*.jpeg")):
            try:
                imageList.append(sizeFix(base, Image.open(name).convert("RGBA")))
            except OSError:
                print("Omitting " + name)

        if len(imageList):
            break
        print("Cannot find folder or folder contains no images. Please try again: ", end = "")
    
    # Read in amount of images to be placed
    imagesCount = 0
    print("Enter the amount of images to be placed: ", end = "")

    while True:
        try:
            imagesCount = int(input())
            break
        except ValueError:
            print("Incorrect input. Please enter a whole number: ", end = "")

    # Places images from image list onto new image, matching colors of base image as closely as possible
    for i in range(imagesCount):
        pos = findPlacement(base)
        closest = imageList[0]
        closestDiff = imageCompare(base, imageList[0], (pos[0] - imageList[0].size[0]//2, pos[1] - imageList[0].size[1]//2))

        for j in range(1, len(imageList)):
            diff = imageCompare(base, imageList[j], (pos[0] - imageList[j].size[0]//2, pos[1] - imageList[j].size[1]//2))
            if diff < closestDiff:
                closest = imageList[j]
                closestDiff = diff

        placeImage(img, closest, (pos[0] - closest.size[0]//2, pos[1] - closest.size[1]//2))
        if (i + 1) % (imagesCount / 1000) < 1:
            print(f"{i+1} images placed")

    # Saves newly created image
    img.save("Built_Image.png")
    input("Built_Image.png created. Press enter to exit ...\n")