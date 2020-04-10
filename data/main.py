from flickr import mining
from downloader import download_images
import os
import time

all_tags = ["waterfall"]
image_per_tag = 10


def download():
    for tag in all_tags:
        print("Getting urls for", tag)
        urls = mining(tag, image_per_tag)
        print("urls = ", urls)
        print("Downloading image for", tag)
        path = os.path.join("data", tag)

        download_images(urls, path)


print("start")
start_time = time.time()
download()
