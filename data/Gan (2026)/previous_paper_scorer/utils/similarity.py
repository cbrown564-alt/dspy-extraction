from difflib import SequenceMatcher
from rapidfuzz import fuzz

def similarity_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()

def best_match_index(input, target_list):
    best_match_num = 0
    highest_similarity = 0
    for ii, target in enumerate(target_list):
        similarity = similarity_ratio(input, target)
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match_num = ii
    return best_match_num



# def fuzz_similarity_ratio(a, b):
#     return fuzz.partial_ratio(a, b)

# def is_all_of_geo_type(text, geo_list, threshold=80):
#     if not text.lower().startswith("all "):
#         return False

#     target = text[4:].lower()  # 去掉 "all "
#     for geo in geo_list:
#         geo_clean = geo.lower()
#         ratio = fuzz_similarity_ratio(target, geo_clean)
#         if ratio >= threshold:
#             return True
#     return False



import re
from rapidfuzz import fuzz, process

def normalize_geo_text(text):
    """
    Lowercase, remove punctuation except inside parentheses, trim whitespace.
    """
    text = text.lower()
    text = re.sub(r'\(.*?\)', '', text)  # remove anything in parentheses
    text = re.sub(r'[^a-z\s]', '', text)  # remove non-alpha except spaces
    return text.strip()

def extract_core_geo(text):
    """
    Combine outside and inside parentheses into one string.
    E.g. 'LADs (Local Authority Districts)' ➝ 'lads local authority districts'
    """
    base = re.sub(r'\(.*?\)', '', text).strip()
    match = re.search(r'\((.*?)\)', text)
    inside = match.group(1) if match else ''
    return f"{base} {inside}".lower().strip()

def is_all_of_geo_type(input_text, geo_list, threshold=85):
    """
    Check if input_text is like 'all X' and matches semantically to any geo type in geo_list.
    Returns matched geo types.
    """
    if not input_text or not input_text.lower().startswith("all "):
        return False, -1   

    target = normalize_geo_text(input_text[4:])  # remove 'all ' and normalize

    candidates = []
    for i, geo in enumerate(geo_list):
        name_core = extract_core_geo(geo)  # e.g. "Local Authority Districts"
        norm_geo = normalize_geo_text(name_core)
        score = fuzz.token_sort_ratio(target, norm_geo)
        if score >= threshold:
            return True, i
    return False, -1        