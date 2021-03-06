import flickr_api
from flickr_api.api import flickr
import json
import requests
import csv
import numpy as np 
import time





class FlickrPhotos():

    def __init__(self):
        flickr_api.set_keys(api_key = '2c0bf9ef96955f21d833728a05ac2926', api_secret = '314d90a562e65882')
        flickr.set_auth_handler("auth.txt")
        flickr_api.enable_cache()

    #Returns photos of a location sorted by views
    def get_photos(self,location, tag=[], r='0.5',text="", count=100):
        photos = flickr.photos.search(
            text=text,tags=tag, 
            lat=str(location[0]), 
            lon=str(location[1]), 
            radius='0.5',
            format='json', 
            nojsoncallback=1, 
            extras=['geo,url_o,views,tags,description'],
            per_page=count,
            privacy_filter=1
        )
        photos = json.loads(photos.decode('utf8'))
        if (int(photos['photos']['total']) <= 10):
            print(photos['photos']['total'])
            photos = flickr.photos.search(
                tags=tag, 
                lat=str(location[0]), 
                lon=str(location[1]), 
                radius='1',
                format='json', 
                nojsoncallback=1, 
                extras=['geo,url_o,views,tags,description'],
                per_page=count,
                privacy_filter=1
            )
            photos = json.loads(photos.decode('utf8'))
        #photos["photos"]["photo"] = sorted(photos["photos"]["photo"], key = lambda i: int(i['views']), reverse=True)
        return photos["photos"]["photo"]

    #Returns the URLS only
    def get_urls(self,photos, max=10):
        urls = []
        for x in photos:
            if('url_o' in x.keys()):
                urls.append(x['url_o'])
        return urls[:10]

    #Return information about photos such as aperture
    def get_info(self,photo):
        info = flickr.photos.getExif(photo_id=photo['id'],format='json', nojsoncallback=1)
        info = json.loads(info)
        return info

    #Return Comments about a photo
    def get_comments(self,photo):
        comm = flickr.photos.comments.getList(photo_id=photo['id'],format='json', nojsoncallback=1)
        comm = json.loads(comm)
        comments = [x["_content"] for x in comm['comments']['comment']]
        return comments


    #Possible function for datamining
    def data_mine(self,location, tag=[], r='0.5',text="",count=100):
        photos = self.get_photos(location, tag=tag,r=r,text=text,count=count)
        photos['urls'] = self.get_urls(photos,max=count)
        for p in photos:
            p['comments'] = self.get_comments(p)
            p['Exif'] = self.get_info(p)
    
    
