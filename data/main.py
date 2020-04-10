from flickr import get_urls
from downloader import download_images
import os
import time

all_species = ["waterfall"]
image_per_specie = 10


def download():
    for specie in all_species:
        print("Getting urls for", specie)
        urls = get_urls(specie, image_per_specie)
        print("urls = ", urls)
        print("Downloading image for", specie)
        path = os.path.join("data", specie)

        download_images(urls, path)


print("start")
start_time = time.time()
download()
