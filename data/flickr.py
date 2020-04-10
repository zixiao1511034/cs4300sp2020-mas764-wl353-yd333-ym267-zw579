from flickrapi import FlickrAPI
import json

KEY = "2c0bf9ef96955f21d833728a05ac2926"
SECRET = "314d90a562e65882"

SIZES = ["url_o", "url_k", "url_h", "url_l", "url_c"]


def get_photos(image_tag):
    extras = ",".join(SIZES)
    flickr = FlickrAPI(KEY, SECRET)
    photos = flickr.photos.search(
        text=image_tag,
        extras=extras,
        privacy_filter=1,
        per_page=50,
        sort="relevance",
        format="json",
    )
    photos = photos.lstrip("jsonFlickrApi(".encode())
    photos = photos.rstrip(")".encode())
    # parsed_text = json.loads(photos)
    # print(parsed_text)
    # for p in parsed_text["photos"]["photo"]:
    # print("id = ", p["id"])
    return photos


def get_url(photo):
    print(photo)
    for i in range(len(SIZES)):
        url = photo.get(SIZES[i])
        if url:
            return url


def get_urls(image_tag, max):
    photos = get_photos(image_tag)
    parsed_text = json.loads(photos)
    counter = 0
    urls = []
    for photo in parsed_text["photos"]["photo"]:
        if counter < max:
            url = get_url(photo)
            if url:
                urls.append(url)
                counter += 1
            # get comments

        else:
            break
    return urls
