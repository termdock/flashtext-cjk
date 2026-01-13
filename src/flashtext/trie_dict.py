import collections

def add_keyword_to_trie(trie_dict, keyword, clean_name, case_sensitive, keyword_key='_keyword_'):
    """
    Add a keyword to the trie dictionary.
    
    Args:
        trie_dict (dict): The trie dictionary structure.
        keyword (str): key to add.
        clean_name (str): clean name to map to.
        case_sensitive (bool): if True, use exact case; otherwise, use mixed case support.
        keyword_key (str): key used to store the clean name at the leaf.
    
    Returns:
        bool: True if a new term was added (didn't exist before), False otherwise.
    """
    status = False
    if not clean_name and keyword:
        clean_name = keyword

    if keyword and clean_name:
        current_dict = trie_dict
        for char in keyword:
            if case_sensitive:
                current_dict = current_dict.setdefault(char, {})
            else:
                # Loose case: ensure we have a node for this step
                lower = char.lower()
                upper = char.upper()
                
                # Try to find existing node (shared)
                next_node = current_dict.get(lower) or current_dict.get(upper)
                if next_node is None:
                    next_node = {}
                
                # Link both lower and upper to this node
                current_dict[lower] = next_node
                current_dict[upper] = next_node
                
                current_dict = next_node
        
        if keyword_key not in current_dict:
            status = True
        
        if isinstance(clean_name, list):
             current_dict[keyword_key] = list(clean_name)
        else:
             current_dict[keyword_key] = clean_name
    return status

def remove_keyword_from_trie(trie_dict, keyword, keyword_key='_keyword_'):
    """
    Remove a keyword from the trie dictionary.
    
    Args:
        trie_dict (dict): The trie dictionary structure.
        keyword (str): keyword to remove.
        keyword_key (str): key used to store the clean name at the leaf.
        
    Returns:
        bool: True if the keyword was removed, False if not found.
    """
    status = False
    if keyword:
        # Note: We do NOT lower the keyword even if case_sensitive is False.
        # Because the Trie now contains edges for both cases.
        current_dict = trie_dict
        character_trie_list = []
        for letter in keyword:
            if letter in current_dict:
                character_trie_list.append((letter, current_dict))
                current_dict = current_dict[letter] # This is safe
            else:
                # if character is not found, break out of the loop
                current_dict = None
                break
        # remove the characters from trie dict if there are no other keywords with them
        if current_dict and keyword_key in current_dict:
            # we found a complete match for input keyword.
            character_trie_list.append((keyword_key, current_dict))
            character_trie_list.reverse()

            for key_to_remove, dict_pointer in character_trie_list:
                if len(dict_pointer.keys()) == 1:
                    dict_pointer.pop(key_to_remove)
                else:
                    # more than one key means more than 1 path.
                    # Delete not required path and keep the other
                    
                    # Check for multi-edge (mixed case) redundancy
                    # If we are removing 'a', check if 'A' points to the same object
                    if isinstance(key_to_remove, str): # Verify it's not _keyword_
                        lower = key_to_remove.lower()
                        upper = key_to_remove.upper()
                        other_key = upper if key_to_remove == lower else lower
                        
                        if other_key != key_to_remove and other_key in dict_pointer and key_to_remove in dict_pointer:
                            if dict_pointer[other_key] is dict_pointer[key_to_remove]:
                                dict_pointer.pop(other_key)

                    dict_pointer.pop(key_to_remove)
                    # After popping, check if dict became empty? 
                    if len(dict_pointer) == 0:
                         continue # Continue bubbling up
                    break
            # successfully removed keyword
            status = True
    return status

def get_all_keywords(trie_dict, term_so_far='', current_dict=None, keyword_key='_keyword_'):
    """
    Recursively builds a dictionary of keywords present in the trie.
    
    Args:
        trie_dict (dict): The root trie dictionary (or current node).
        term_so_far (str): term built so far.
        current_dict (dict): recursion helper.
        keyword_key (str): key used to store the clean name.
        
    Returns:
        dict: map of keyword -> clean_name
    """
    terms_present = {}
    if not term_so_far:
        term_so_far = ''
    if current_dict is None:
        current_dict = trie_dict
        
    if current_dict is None:
        return terms_present
    
    # Optimization: group keys pointing to the same child node object
    # to avoid exponential traversal in Mixed Case Support (DAG Trie)
    visited_children = {} # id(child_node) -> child_node
    keys_for_child = {}   # id(child_node) -> set(keys) OR representative_key
    
    for key in current_dict:
        if key == keyword_key:
            terms_present[term_so_far] = current_dict[key]
        else:
            child_node = current_dict[key]
            child_id = id(child_node)
            if child_id not in visited_children:
                visited_children[child_id] = child_node
                keys_for_child[child_id] = key # Pick first key as representative
            # Else: we skip traversing this child again for other keys (e.g. 'A' vs 'a')
    
    for child_id, child_node in visited_children.items():
        representative_key = keys_for_child[child_id]
        # Use representative key to recurse. 
        sub_values = get_all_keywords(None, term_so_far + representative_key, child_node, keyword_key)
        for key in sub_values:
            terms_present[key] = sub_values[key]
    return terms_present
