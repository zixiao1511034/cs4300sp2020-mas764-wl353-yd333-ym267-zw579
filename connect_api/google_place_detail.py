import requests
import json
import googlemaps
from geopy.distance import geodesic
import os
from dotenv import load_dotenv

load_dotenv()


class GooglePlaces(object):
    def __init__(self, query):
        super(GooglePlaces, self).__init__()
        self.apiKey = os.getenv("APIKEY")
        self.query = query
        self.fields = ["name", "geometry", "place_id", "rating", "review"]
        self.types = ["tourist_attraction"]
        self.radius = None
        self.coordinates = None
        self.json_file = {}
        self.get_coordinates_radius(query)
        self.get_json

    def get_coordinates_radius(self, query):
        gmaps = googlemaps.Client(key=self.apiKey)
        geocode_result = gmaps.geocode(self.query)
        lat = geocode_result[0]["geometry"]["location"]["lat"]
        lng = geocode_result[0]["geometry"]["location"]["lng"]
        southwest_lng = geocode_result[0]["geometry"]["bounds"]["southwest"]["lng"]
        southwest_lat = geocode_result[0]["geometry"]["bounds"]["southwest"]["lat"]
        northeast_lng = geocode_result[0]["geometry"]["bounds"]["northeast"]["lng"]
        northeast_lat = geocode_result[0]["geometry"]["bounds"]["northeast"]["lat"]
        southwest = (southwest_lat, southwest_lng)
        northeast = (northeast_lat, northeast_lng)

        self.coordinates = str(lat) + ", " + str(lng)
        radius = int(geodesic(southwest, northeast).meters // 4)
        if radius > 50000:
            radius = "50000"
        self.radius = str(radius)

    def search_places_by_coordinate(self, location, radius):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        places = []
        params = {
            "location": location,
            "radius": radius,
            "types": self.types,
            "key": self.apiKey,
        }
        res = requests.get(endpoint_url, params=params)
        results = json.loads(res.content)

        places.extend(results["results"])
        return places

    def get_place_details(self, place_id):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "placeid": place_id,
            "fields": ",".join(self.fields),
            "key": self.apiKey,
        }
        res = requests.get(endpoint_url, params=params)
        place_details = json.loads(res.content)
        return place_details

    def get_json(self):
        places = self.search_places_by_coordinate(self.coordinates, self.radius)
        for place in places:
            details = self.get_place_details(place["place_id"])
            self.json_file[details["result"]["name"]] = details

        json_file = json.dumps(self.json_file, indent=2)
        with open("google-review.json", "w") as outfile:
            outfile.write(json_file)
        return self.json_file


# query = input("Please input a city/area: ")
# api = GooglePlaces(query)
# json_file = api.get_json()
