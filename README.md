# Image Builder

Image Builder is a web app that allows you to build cool new images from images you already have. Simply provide a few images and numbers and let Image Builder do the rest.

## Features

- Mosaic-like image composer which re-creates an image using several other images (main feature)
- Image resizer that can scale an image to any dimensions
- Support for many common image formats such as PNG and JPEG
- Simple and responsive design that works on any device

## Technologies

Image Builder is built with the following technologies:

- HTML, CSS, and JavaScript for the frontend
- Python and Flask for the backend
- OpenCV (cv2) for image processing and manipulation

## Demo

You can try out Image Builder at <https://www.darim.me/ImageBuilder>. Please note that the Image Builder API is being hosted on a relatively slow server (free service), so image generation may take some time.

## Installation

To run Image Builder locally, you need to have Python installed on your machine. Then, follow these steps:

- Clone this repository:

```
git clone https://github.com/DarimK/ImageBuilder.git
```

- Navigate to the project folder:

```
cd ImageBuilder
```

- Install the dependencies:

```
pip install -r requirements.txt
```

- Start the API:

```
python app.py
```

- Open the index.html file:

```
./client/index.html
```

###### :)