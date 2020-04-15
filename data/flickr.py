from flickrapi import FlickrAPI
import json

KEY = "<KEY>"
SECRET = "<SECRET>"

SIZES = ["url_o", "url_k", "url_h", "url_l", "url_c"]

flickr = FlickrAPI(KEY, SECRET)
def get_photos(image_tag):
    extras = ",".join(SIZES)
    
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
    for i in range(len(SIZES)):
        url = photo.get(SIZES[i])
        if url:
            return url


def mining(image_tag, max):
    photos = get_photos(image_tag)
    parsed_text = json.loads(photos)
    counter = 0
    urls = []
    for photo in parsed_text["photos"]["photo"]:
        if counter < max:
            url = get_url(photo)
            get_info(photo)
            get_comments(photo)
            if url:
                urls.append(url)
                counter += 1

        else:
            break
    return urls


def get_info(photo):
    photo_id = photo['id']
    text = flickr.photos.getInfo(photo_id=photo_id, format='json')
    text = text.lstrip('jsonFlickrApi('.encode())
    text = text.rstrip(')'.encode())
    parsed_data = json.loads(text)
    # print("Photo Info:")
    # print(parsed_data)
    # print(" ")


def get_comments(photo):
    photo_id = photo['id']
    text = flickr.photos.comments.getList(photo_id=photo_id, format='json')
    text = text.lstrip('jsonFlickrApi('.encode())
    text = text.rstrip(')'.encode())
    parsed_data = json.loads(text)
    print("Photo Comments:")
    print(parsed_data)
    print(" ")

