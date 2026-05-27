import re

stop_words = [
    'a', 'an', 'the', 'and', 'or', 'but', 'if', 'while', 'with', 'of', 'at', 'by',
    'for', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
    'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
    'can', 'will', 'just', 'don', 'should', 'now', 'is', 'am', 'are', 'was', 'were',
    'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'having'
]



def clean_token(token):
    return re.sub(r'\W+', '', token.lower()) 

def clean_and_split_tokens(string):
    return [clean_token(t) for t in string.split() if t.lower() not in stop_words]





