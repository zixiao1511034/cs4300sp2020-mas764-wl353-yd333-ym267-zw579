import json
import re
import numpy as np
from boolean_search import build_inverted_index, dis_boolean_search_ordered, rank_places
from google_place_detail import GooglePlaces
import time
from nltk.stem import PorterStemmer
from flickr import FlickrPhotos


query = input("Please input a city/area: ")
query_terms = input("Please input topic: ").split(" ")
start = time.time()
api = GooglePlaces(query)
json_review_dict = api.get_json()
print(api.radius)


"""
PROCESS JSON:
"""
# with open("google-review.json", "r") as f:
#     json_review_dict = json.load(f)
# json_review_dict = json.loads(json_file)

## Some ideas for the future:
# We can rank reviews further by how recent they are and by user-ranking (social component?).
# We can tokenize in a way that accommodates typos or does better punctuation/space filtering.

# Build dict with relevant fields: place ids, coordinate dict, and tokenized comments.
ps = PorterStemmer()
review_dict = {}
review_list = []
for place in json_review_dict:
    if "reviews" in json_review_dict[place]["result"]:
        review_dict[place] = {}
        # I am assuming the key for each place is same as place name for
        # the purposes of later computations.
        review_dict[place]["name"] = json_review_dict[place]["result"]["name"]
        review_dict[place]["id"] = json_review_dict[place]["result"]["place_id"]
        review_dict[place]["loc_dict"] = json_review_dict[place]["result"]["geometry"]
        review_dict[place]["comment_toks"] = []
        for review in json_review_dict[place]["result"]["reviews"]:
            # we can modify this in the future for multi-language support:
            if review.get("language") == "en":
                comment = review["text"]
                # Tokenize: Get rid of new line token!!
                comment = comment.lower()
                tokens = re.findall("[a-z]+", comment)
                stem_tokens = list(set([ps.stem(t) for t in tokens]))
                # combining all comment toks.
                # If we decide to treat comments seperately, will change this part.
                review_dict[place]["comment_toks"] += stem_tokens


        review_list.append(review_dict[place].copy())


"""
PROCESS PREFERENCE QUERY:
"""
# TODO: Create tokenized list of query_terms.
# For now I am using an example:
# query_terms = ["waterfall", "park", "winter", "trail"]

stem_query_terms = list(set([ps.stem(q) for q in query_terms]))
print(stem_query_terms)

"""
APPLY METHODS:
"""
inverted_index = build_inverted_index(review_list)
bool_search_results = dis_boolean_search_ordered(
    stem_query_terms, inverted_index, len(review_list)
)
ranked_places = rank_places(review_dict, review_list, bool_search_results)



FP = FlickrPhotos()
place_url = {}
for r_p in ranked_places:
    photos = FP.get_photos(location=[r_p["loc_dict"]["location"]["lat"], r_p["loc_dict"]["location"]["lng"]])
    urls = FP.get_urls(photos)
    place_url[r_p["name"]] = urls


end = time.time()
for place in ranked_places:
    print(place["name"])

print(place_url)
print("/////////////running time:{time}sec".format(time=end - start))
