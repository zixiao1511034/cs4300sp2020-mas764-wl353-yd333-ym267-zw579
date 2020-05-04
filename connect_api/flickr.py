import flickr_api
from flickr_api.api import flickr
import json
import requests
import csv
import numpy as np 
import time
import os
from geopy.distance import geodesic
from dotenv import load_dotenv


load_dotenv()


class FlickrPhotos():

    def __init__(self):
        dir = os.path.abspath(os.path.dirname(__file__))
        auth_file_name = os.path.join(dir, 'auth.txt')
        flickr_api.set_keys(api_key = os.getenv("F_APIKEY"), api_secret = os.getenv("F_SECRET"))
        flickr.set_auth_handler(auth_file_name)
        flickr_api.enable_cache()

    #Returns photos of a location sorted by views
    def get_photos(self, location=[], tag=[], r='0.5',text="", count=100):
        photos = flickr.photos.search(
            # tags=tag, 
            text=text,
            # lat=str(location[0]), 
            # lon=str(location[1]), 
            # radius='0.5',
            format='json', 
            nojsoncallback=1, 
            extras=['geo,url_o,views,tags,description,url_z'],
            per_page=count,
            sort="relevance",
            has_geo=1,
            privacy_filter=1
        )
        photos = json.loads(photos.decode('utf8'))
        p = photos["photos"]['photo']
        l1 = (location[0],location[1])
        for x in p:
            g = geodesic(l1, (x['latitude'],x['longitude']))
            x['dist'] = g
        #photos["photos"]["photo"] = sorted(photos["photos"]["photo"], key = lambda i: int(i['views']), reverse=True)
        return p

    #Returns the URLS only
    def get_urls(self,photos, max=10):
        urls = []
        for x in photos[:10]:
            if('url_z' in x.keys() and x['dist'] <= 1.0):
                urls.append(x['url_z'])
        return urls

    #Return information about photos such as aperture
    def get_info(self,photo):
        info = flickr.photos.getExif(photo_id=photo['id'],format='json', nojsoncallback=1)
        info = json.loads(info)
        # print(json.dumps(info, indent=2))
        return info

    #Return URL with info
    def get_urls_info(self,photos, max=10):
        urls_info = []
        for x in photos[:10]:
            if('url_z' in x.keys()):
                info = self.get_info(x)
                # print(info.keys())
                if 'photo' in info.keys():
                    URL = x['url_z']
                    CAMERA = info['photo']['camera']
                    SS = AP = ISO = EB = None
                    for tag in info['photo']['exif']:
                        if tag['label'] == 'Exposure': SS = tag['raw']['_content']
                        if tag['label'] == 'Aperture': AP = tag['clean']['_content']
                        if tag['label'] == 'ISO Speed': ISO = tag['raw']['_content']
                        if tag['label'] == 'Exposure Bia': EB = tag['clean']['_content']
                        
                    comb = {'url': URL, 
                            'camera': CAMERA, 
                            'SS':SS, 
                            'AP':AP,
                            'ISO':ISO,
                            'EB':EB }
                    urls_info.append(comb)
                    time.sleep(0.05)
                    # print("------------------------------------")
        return urls_info

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
    
    
