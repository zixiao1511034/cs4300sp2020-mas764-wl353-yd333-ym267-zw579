import json
import re
import numpy as np
from boolean_search import build_inverted_index, dis_boolean_search_ordered, rank_places

"""
PROCESS JSON:
"""
with open('google-review.json', 'r') as f:
    json_review_dict = json.load(f)

## Some ideas for the future:
# We can rank reviews further by how recent they are and by user-ranking (social component?).
# We can tokenize in a way that accommodates typos or does better punctuation/space filtering.

# Build dict with relevant fields: place ids, coordinate dict, and tokenized comments.
review_dict = {}
review_list = []
for place in json_review_dict:
    if 'reviews' in json_review_dict[place]['result']:
        review_dict[place] = {}
        # I am assuming the key for each place is same as place name for
        # the purposes of later computations.
        review_dict[place]['name'] = json_review_dict[place]['result']['name']
        review_dict[place]['id'] = json_review_dict[place]['result']['place_id']
        review_dict[place]['loc_dict'] = json_review_dict[place]['result']['geometry']
        review_dict[place]['comment_toks'] = []
        for review in json_review_dict[place]['result']['reviews']:
            # we can modify this in the future for multi-language support:
            if review.get('language') == "en":
                comment = review['text']
                # Tokenize: Get rid of new line token!!
                comment = comment.lower()
                tokens = re.findall('[a-z]+',comment)
                # combining all comment toks.
                # If we decide to treat comments seperately, will change this part.
                review_dict[place]['comment_toks']+=tokens
        review_list.append(review_dict[place].copy())
# print(type(review_list[0]))

"""
PROCESS PREFERENCE QUERY:
"""
# TODO: Create tokenized list of query_terms.
# For now I am using an example:
query_terms = ["waterfall", "park", "winter", "trail"]

"""
APPLY METHODS:
"""
inverted_index = build_inverted_index(review_list)
bool_search_results = dis_boolean_search_ordered(query_terms, inverted_index, len(review_list))
ranked_places = rank_places(review_dict, review_list, bool_search_results)
# print(len(ranked_places))
# print(len(review_dict))
# print(len(review_list))
# print(ranked_places[0])
