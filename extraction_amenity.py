import pandas as pd
import re
from fuzzywuzzy import fuzz
from transformers import BertTokenizer, BertTokenizerFast

FUZZY_THRESHOLD = 85
MIN_AMENITY_LENGTH = 5


def is_valid_fuzzy_match(amenity, match, threshold):
    """
    Validates a fuzzy match to reduce false positives.
    """
    return fuzz.partial_ratio(amenity.lower(), match.lower()) >= threshold


def find_amenity_matches(amenity, text, threshold=FUZZY_THRESHOLD):
    """
    Finds all occurrences of an amenity in the text using exact and fuzzy matching.

    :param amenity: The amenity string to search for.
    :param text: The text in which to search.
    :param threshold: The minimum fuzzy matching score to consider a match.
    :return: A list of tuples indicating the start and end positions of matches.
    """
    pattern = re.compile(r'\b' + re.escape(amenity) + r'\b', re.IGNORECASE)
    exact_matches = list(pattern.finditer(text))
    match_positions = [(match.start(), match.end()) for match in exact_matches]

    if not match_positions and (len(amenity) >= MIN_AMENITY_LENGTH):
        # Perform fuzzy matching only if the amenity is sufficiently long
        max_ratio = 0
        best_pos = None
        text_length = len(text)
        window_size = len(amenity)

        for i in range(text_length - window_size + 1):
            window = text[i:i + window_size]
            if is_valid_fuzzy_match(amenity, window, threshold):
                ratio = fuzz.partial_ratio(amenity.lower(), window.lower())
                if ratio > max_ratio:
                    max_ratio = ratio
                    best_pos = (i, i + window_size)

        if max_ratio >= threshold and best_pos is not None:
            match_positions.append(best_pos)

    return match_positions


def extract_context_with_tokens(text, start, end, tokenizer=None, token_window=10):
    """
    Extracts a token-based window of text around the matched amenity.

    :param text: The full text.
    :param start: Start index of the match.
    :param end: End index of the match.
    :param tokenizer: A basic tokenizer function (e.g., str.split). Default is whitespace-based split.
    :param token_window: Number of tokens to include before and after the match.
    :return: A substring containing the context around the match and aligned token offsets.
    """
    if tokenizer is None:
        tokenizer = lambda t: t.split()  # Default tokenizer is whitespace-based split

    tokens = tokenizer(text)
    current_offset = 0
    offsets = []
    for token in tokens:
        token_start = text.find(token, current_offset)
        token_end = token_start + len(token)
        offsets.append((token_start, token_end))
        current_offset = token_end

    # Find the token indices corresponding to the start and end positions
    match_start_token = match_end_token = None
    for i, (token_start, token_end) in enumerate(offsets):
        if token_start <= start < token_end:
            match_start_token = i
        if token_start < end <= token_end:
            match_end_token = i

    if match_start_token is None or match_end_token is None:
        raise ValueError("Match positions do not align with any token offsets.")

    # Calculate token-based context
    context_start = max(match_start_token - token_window, 0)
    context_end = min(match_end_token + token_window + 1, len(tokens))

    return ' '.join(tokens[context_start:context_end])



def pipeline(review_text: str) -> dict:

    amenities = [
        "toilet", "restroom", "bathroom",
        "parking", "car park",
        "dog", "pet",
        "playground", "family", "kid",
        "cafe",
        "cycling", "bike", "bicycle",
        "picnic area", "camping area",
        "gift shop", "convenience store"
    ]

    found_amenities = {}
    # Iterate over each amenity
    for amenity in amenities:
        matches = find_amenity_matches(amenity, review_text)
        if matches:
            found_amenities[amenity] = matches

    for found_amenity, matches in found_amenities.items():
        contexts = []
        for match in matches:
            context = extract_context_with_tokens(text=review_text, start=match[0], end=match[1])
            contexts.append(context)
        found_amenities[found_amenity] = contexts

    return found_amenities

