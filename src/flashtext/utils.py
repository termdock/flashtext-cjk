import re

_white_space_chars = set(['.', '\t', '\n', '\a', ' ', ','])
_keyword = '_keyword_' # Needed for stop criteria? 

# We need to accept keyword_key as param for flexibility
def levensthein(word, max_cost, start_node, white_space_chars=None, keyword_key='_keyword_'):
    """
    Retrieve the nodes where there is a fuzzy match,
    via levenshtein distance, and with respect to max_cost

    Args:
        word (str): word to find a fuzzy match for
        max_cost (int): maximum levenshtein distance when performing the fuzzy match
        start_node (dict): Trie node from which the search is performed
        white_space_chars (set): Characters considered whitespace/boundary for fuzzy stop criteria.
        keyword_key (str): Key used for leaf nodes.

    Yields:
        node, cost, depth (tuple): A tuple containing the final node,
                                  the cost (i.e the distance), and the depth in the trie
    """
    if white_space_chars is None:
        white_space_chars = _white_space_chars
        
    rows = range(len(word) + 1)

    for char, node in start_node.items():
        yield from _levenshtein_rec(char, node, word, rows, max_cost, 1, white_space_chars, keyword_key)


def _levenshtein_rec(char, node, word, rows, max_cost, depth, white_space_chars, keyword_key):
    n_columns = len(word) + 1
    new_rows = [rows[0] + 1]
    cost = 0

    for col in range(1, n_columns):
        insert_cost = new_rows[col - 1] + 1
        delete_cost = rows[col] + 1
        replace_cost = rows[col - 1] + int(word[col - 1] != char)
        cost = min((insert_cost, delete_cost, replace_cost))
        new_rows.append(cost)

    stop_crit = isinstance(node, dict) and node.keys() & (white_space_chars | {keyword_key})
    if new_rows[-1] <= max_cost and stop_crit:
        yield node, cost, depth

    elif isinstance(node, dict) and min(new_rows) <= max_cost:
        for new_char, new_node in node.items():
            yield from _levenshtein_rec(new_char, new_node, word, new_rows, max_cost, depth + 1, white_space_chars, keyword_key)


def extract_sentences_util(text, extract_keywords_func, delimiters=None):
    """
    Extract sentences that contain keywords.
    
    Args:
        text (str): Input text
        extract_keywords_func (callable): Function to extract keywords from a sentence.
        delimiters (list of str): Punctuation to split sentences. 
                                  Default: ['.', '?', '!', ';', '\\n']
    Returns:
        list of (str, list): [(sentence, [keywords]), ...]
    """
    if delimiters is None:
        delimiters = ['.', '?', '!', ';', '\n']
    
    # Sort delimiters by length desc to ensure longest match first if they overlap
    delimiters.sort(key=len, reverse=True)
    
    escaped_delimiters = [re.escape(d) for d in delimiters]
    pattern = '|'.join(escaped_delimiters)
    
    # (pattern) captures the delimiter so we can attach it back
    regex_pattern = '((?:' + pattern + ')+)'
    
    parts = re.split(regex_pattern, text)
    
    sentences_list = []
    # parts structure: [content, delimiter, content, delimiter...]
    for i in range(0, len(parts), 2):
        sentence_content = parts[i]
        delimiter = parts[i+1] if i + 1 < len(parts) else ""
        full_sentence = sentence_content + delimiter
        if full_sentence.strip(): 
             sentences_list.append(full_sentence)
             
    results = []
    for sent in sentences_list:
        keywords = extract_keywords_func(sent)
        if keywords:
            results.append((sent, keywords))
    
    return results
