from progress.bar import Bar
import requests
import os
import sys
import time


def create_folder(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def download_images(urls, path):
    create_folder(path)
    for url in urls:
        image_name = url.split("/")[-1]
        image_path = os.path.join(path, image_name)

        if not os.path.isfile(image_path):
            response = requests.get(url, stream=True)

            with open(image_path, "wb") as outfile:
                outfile.write(response.content)
