import numpy as np

"""
USEFUL METHODS FOR BOOLEAN SEARCH:
"""
def build_inverted_index(msgs):
    """
    Arguments:
        msgs: list of dicts
            each dict in msgs has field 'comment_toks' that contain tokenized
            comments.
    Returns:
        inverted_index: dict
            For each term, the index contains a sorted list of tuples
            (doc_id, count_of_term_in_doc) such that tuples with smaller doc_ids
            appear first:
            inverted_index[term] = [(d1, tf1), (d2, tf2), ...]
    """
    inverted_index = {}
    for i in range(len(msgs)):
        unique_terms = set()
        for token in msgs[i]['comment_toks']:
            unique_terms.add(token)
        for term in unique_terms:
            count_of_term_in_doc = msgs[i]['comment_toks'].count(term)
            entry_tuple = (i, count_of_term_in_doc)
            if inverted_index.get(term):
                inverted_index[term].append(entry_tuple)
            else:
                inverted_index[term] = [entry_tuple]
    # Sort tuples in ascending order of doc_ids for each term in inverted_index:
    for term in inverted_index:
        inverted_index[term] = sorted(inverted_index[term], key = lambda x: x[0])

    return inverted_index


def disjunctive_boolean_search(query_terms, inverted_index):
    """
    Returns all postings regardless of no. of occurence.
    This function is not really necessary for our purposes.
    """
    all_postings = []
    for query_term in query_terms:
        for entry in inverted_index[query_term.lower()]:
            all_postings.append(entry[0])

    disjunctive_list = list(set(all_postings))
    return disjunctive_list


def dis_boolean_search_ordered(query_terms, inverted_index, number_of_docs):
    """
    Arguments:
        query_terms: list of strings
            tokenized user preference query
        inverted_index: dict
            For each term, the index contains
            a sorted list of tuples (doc_id, count_of_term_in_doc)
            such that tuples with smaller doc_ids appear first:
            inverted_index[term] = [(d1, tf1), (d2, tf2), ...]
        number_of_docs: int
            len(msgs)
    Returns:
        result: list of ints
            Elements are indexes of docs containing highest no. of user terms
    """
    query_postings = {}

    for query_term in query_terms:
        query_term = query_term.lower()
        query_postings[query_term] = []
        for entry in inverted_index[query_term]:
            # For now, I disregarded term frequency of individual terms.
            query_postings[query_term].append(entry[0])

    # To hold number of user terms each comment has:
    docs = np.zeros(number_of_docs, dtype=int)
    for query_term in query_postings:
        for posting in query_postings[query_term]:
            docs[posting] += 1

    # sort negated array so no. of occurences are in descending order
    indices_to_sort = np.argsort(-docs)
    results = []
    for index in indices_to_sort:
        if docs[index] == 0:
            break # we don't need to keep going after running out of relevant comments
        results.append(index)
    return results


def rank_places(rev_dict, msgs_list, ordered_dis_bool_search_results):
    """
    Accesses place dicts using indices given by ordered boolean search.
    Arguments:
        rev_dict: nested dict of places
        msgs_list: list of place dicts
        ordered_dis_bool_search_results: list of int
            return value of _dis_boolean_search_ordered() described above.
    Precondition:
        'name' field in elements of msgs_list should correspond to keys in rev_dict.
    Return:
        ranked_places: list of dicts
    """
    ranked_places = []
    for doc_index in ordered_dis_bool_search_results:
        place_dict = msgs_list[doc_index]
        place_name = place_dict['name']
        ranked_places.append(rev_dict[place_name])
    return ranked_places
