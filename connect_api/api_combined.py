import json
import re
import numpy as np
from boolean_search import build_inverted_index, dis_boolean_search_ordered, rank_places
from google_place_detail import GooglePlaces
import time
from nltk.stem import PorterStemmer
from flickr import FlickrPhotos
import difflib

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


class IRApi:
    def __init__(self, city, topic):
        self.place_url_review = []
        self.city = city
        self.ps = PorterStemmer()
        self.topic = topic.split(" ")
        self.stem_topic = list(set([self.ps.stem(t) for t in topic.split(" ")]))
        self.variation_topic = {}

    def get_review(self):
        self.GP = GooglePlaces(self.city)
        return self.GP.get_json()

    def process_json(self):
        self.json_review_dict = self.get_review()
        # print(self.json_review_dict)
        self.review_dict = {}
        self.review_list = []
        for place in self.json_review_dict:
            if "reviews" in self.json_review_dict[place]["result"]:
                self.review_dict[place] = {}
                # I am assuming the key for each place is same as place name for
                # the purposes of later computations.
                self.review_dict[place]["name"] = self.json_review_dict[place]["result"]["name"]
                self.review_dict[place]["id"] = self.json_review_dict[place]["result"]["place_id"]
                self.review_dict[place]["loc_dict"] = self.json_review_dict[place]["result"]["geometry"]
                self.review_dict[place]["comment_toks"] = []
                for review in self.json_review_dict[place]["result"]["reviews"]:
                    # we can modify this in the future for multi-language support:
                    if review.get("language") == "en":
                        comment = review["text"]
                        # Tokenize: Get rid of new line token!!
                        comment = comment.lower()
                        tokens = re.findall("[a-z]+", comment)
                        stem_tokens = list(set([self.ps.stem(t) for t in tokens]))
                        # combining all comment toks.
                        # If we decide to treat comments seperately, will change this part.
                        self.review_dict[place]["comment_toks"] += stem_tokens


                self.review_list.append(self.review_dict[place].copy())

    def get_rank_places(self):
        self.process_json()
        inverted_index = build_inverted_index(self.review_list)
        bool_search_results = dis_boolean_search_ordered(
            self.stem_topic, inverted_index, len(self.review_list)
        )
        ranked_places = rank_places(self.review_dict, self.review_list, bool_search_results)

        FP = FlickrPhotos()
        # print(ranked_places)
        for r_p in ranked_places:
            photos = FP.get_photos(location=[r_p["loc_dict"]["location"]["lat"], r_p["loc_dict"]["location"]["lng"]], text=r_p["name"])
            # photos = FP.get_photos(text=r_p['name'])

            urls = FP.get_urls(photos)
            reviews = [rv['text'] for rv in self.json_review_dict[r_p["name"]]["result"]["reviews"]]
            self.place_url_review.append({"name": r_p["name"], "images": urls, "reviews": reviews})

        self.highlight(self.place_url_review)
        return self.place_url_review


    def highlight(self, place_url_review):
        highlight_pos = []
        for place in place_url_review:

            for review_i, review in enumerate(place['reviews']):
                review_split = review.split()
                for word_i, word in enumerate(review_split):
                    if word[-1] in ",.!?:":
                        word_ = word[:-1]
                        for topic in self.stem_topic:
                            if self.ps.stem(word_) == topic:
                                highlight_pos.append((review_i, word_i, word_))
                                review_split[word_i] = "<b>" + word_ + "</b>" + word[-1]
                    else:
                        for topic in self.stem_topic:
                            if self.ps.stem(word) == topic:
                                highlight_pos.append((review_i, word_i, word))
                                review_split[word_i] = "<b>" + word + "</b>"
                place["reviews"][review_i] = (" ".join(review_split))
        print(highlight_pos)
        return

if __name__ == '__main__':
    #input city/area name string, as specific as possible. Eg. "Manhattan, New York"
    city = input("Please input a city/area: ")
    #input topic, seperated by space. Eg. "photo historical building bridge"
    topic = input("Please input topic: ")

    IR = IRApi(city, topic)
    place_url = json.dumps(IR.get_rank_places(), indent=2)
    print(place_url)


