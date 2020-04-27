import json
import re
import numpy as np
from boolean_search import build_inverted_index, dis_boolean_search_ordered, rank_places
from google_place_detail import GooglePlaces
import time
import nltk
from nltk.stem import PorterStemmer
from flickr import FlickrPhotos
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os

class IRApi:
    def __init__(self, city, topic):
        dir = os.path.abspath(os.path.dirname(__file__))
        nltk.data.path.append(dir)
        self.place_url_review = []
        self.city = city
        self.ps = PorterStemmer()
        self.stem_topic = list(set([self.ps.stem(t) for t in topic.split(" ")]))

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
        analyzer = SentimentIntensityAnalyzer()
        FP = FlickrPhotos()
        # print(ranked_places)
        for r_p in ranked_places:
            photos = FP.get_photos(location=[r_p["loc_dict"]["location"]["lat"], r_p["loc_dict"]["location"]["lng"]], text=r_p["name"])
            # photos = FP.get_photos(text=r_p['name'])

            urls = FP.get_urls(photos)
            reviews = []
            reviews = [rv['text'] for rv in self.json_review_dict[r_p["name"]]["result"]["reviews"]]
            
            sentiment = {}
            s = [analyzer.polarity_scores(rv['text']) for rv in self.json_review_dict[r_p["name"]]["result"]["reviews"]]
            x = np.argmax([x['compound'] for x in s])
            sentiment['most_positive'] = (reviews[x],s[x]['compound'])
            x = np.argmin([x['compound'] for x in s])
            sentiment['most_negative'] = (reviews[x],s[x]['compound'])
            sentiment['avg_sentiment'] = np.mean([x['compound'] for x in s])
            if(sentiment['avg_sentiment'] < 0.05):
                sentiment['overall'] = 'negative'
            elif(sentiment['avg_sentiment'] > 0.05):
                sentiment['overall'] = 'positve'
            else:
                sentiment['overall'] = 'neutral'

            self.place_url_review.append({"name": r_p["name"], "images": urls, "reviews": reviews, "sentiment":sentiment})
        return self.place_url_review




if __name__ == '__main__':
    #input city/area name string, as specific as possible. Eg. "Manhattan, New York"
    city = input("Please input a city/area: ")
    #input topic, seperated by space. Eg. "photo historical building bridge"
    topic = input("Please input topic: ")

    IR = IRApi(city, topic)
    place_url = json.dumps(IR.get_rank_places(), indent=2)
    print(place_url)


