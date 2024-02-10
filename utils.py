import random
import re
from fuzzywuzzy import fuzz
import time


def normalize_string(s):
    legal_entities = ['llc', 'inc', 'ltd', 'corporation', 'corp', 'lp']
    s = s.lower().replace('&', 'and').replace('.', '').replace(',', '')
    for entity in legal_entities:
        s = s.replace(entity, '')
    # Remove non-alphanumeric characters and extra spaces
    s = ''.join(char for char in s if char.isalnum() or char.isspace())
    s = ' '.join(s.split())  # Removes extra whitespace
    return s


def remove_word(original_string, word_to_remove):
    """
    Removes a specified word from a given string.
    :param original_string: The string from which to remove the word.
    :param word_to_remove: The word to remove.
    :return: String with the specified word removed.
    """
    pattern = r'\b' + re.escape(word_to_remove) + r'\b'
    return re.sub(pattern, '', original_string, flags=re.IGNORECASE).strip()




def is_exact_match(title, search_term):
    """
    Checks if the title is an exact match of the search term after normalization.
    :param title: The title of the business.
    :param search_term: The search term to match.
    :return: True if the title is an exact match of the normalized search term, False otherwise.
    """
    normalized_title = normalize_string(title)
    normalized_search_term = normalize_string(search_term)
    
    return normalized_title == normalized_search_term


def random_delay(min_seconds=1, max_seconds=3):
    """
    Introduces a random delay between requests.
    :param min_seconds: Minimum delay in seconds.
    :param max_seconds: Maximum delay in seconds.
    """
    time.sleep(random.uniform(min_seconds, max_seconds))

# def contains_all_search_terms(title, search_term):
#     title_lower = title.lower()
#     search_terms_lower = search_term.lower().split()
#     return all(word in title_lower for word in search_terms_lower)


def contains_all_search_terms(title, search_term):
    title_normalized = normalize_string(title)
    search_terms_normalized = normalize_string(search_term)
    search_terms_lower = search_terms_normalized.split()
    return all(word in title_normalized for word in search_terms_lower)

USER_AGENTS = [
    # Windows Browsers - Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",  # Chrome on Windows 10
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36",  # Older Chrome on Windows 7
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",  # Newer Chrome on Windows 10

    # Windows Browsers - Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",  # Firefox on Windows 10
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0",  # Older Firefox on Windows 7
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",  # Newer Firefox on Windows 10

    # Windows Browsers - Internet Explorer
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",  # Internet Explorer 11 on Windows 10
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",  # Internet Explorer 8 on Windows Vista

    # Windows Browsers - Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/90.0.818.56",  # Edge on Windows 10
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.309.65 Safari/537.36 Edge/18.19041",  # Older Edge on Windows 10
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",  # Newer Edge on Windows 10

    # Additional Browsers - Opera
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.172"  # Opera on Windows 10
]



def random_user_agent():
    """
    Returns a random User-Agent string.
    """
    return random.choice(USER_AGENTS)
