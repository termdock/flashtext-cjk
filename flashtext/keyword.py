import os
import string
import io
import json
import re





from .trie_dict import add_keyword_to_trie, remove_keyword_from_trie, get_all_keywords
from .utils import levensthein, extract_sentences_util


class KeywordProcessor(object):
    """KeywordProcessor

    Attributes:
        _keyword (str): Used as key to store keywords in trie dictionary.
            Defaults to '_keyword_'
        non_word_boundaries (set(str)): Characters that will determine if the word is continuing.
            Defaults to set([A-Za-z0-9_])
        keyword_trie_dict (dict): Trie dict built character by character, that is used for lookup
            Defaults to empty dictionary
        case_sensitive (boolean): if the search algorithm should be case sensitive or not.
            Defaults to False

    Examples:
        >>> # import module
        >>> from flashtext import KeywordProcessor
        >>> # Create an object of KeywordProcessor
        >>> keyword_processor = KeywordProcessor()
        >>> # add keywords
        >>> keyword_names = ['NY', 'new-york', 'SF']
        >>> clean_names = ['new york', 'new york', 'san francisco']
        >>> for keyword_name, clean_name in zip(keyword_names, clean_names):
        >>>     keyword_processor.add_keyword(keyword_name, clean_name)
        >>> keywords_found = keyword_processor.extract_keywords('I love SF and NY. new-york is the best.')
        >>> keywords_found
        >>> ['san francisco', 'new york', 'new york']

    Note:
        * loosely based on `Aho-Corasick algorithm <https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm>`_.
        * Idea came from this `Stack Overflow Question <https://stackoverflow.com/questions/44178449/regex-replace-is-taking-time-for-millions-of-documents-how-to-make-it-faster>`_.
    """

    def __init__(self, case_sensitive=False):
        """
        Args:
            case_sensitive (boolean): Keyword search should be case sensitive set or not.
                Defaults to False
        """
        self._keyword = '_keyword_'
        self._white_space_chars = set(['.', '\t', '\n', '\a', ' ', ','])
        try:
            # python 2.x
            self.non_word_boundaries = set(string.digits + string.letters + '_')
        except AttributeError:
            # python 3.x
            self.non_word_boundaries = set(string.digits + string.ascii_letters + '_')
        self.keyword_trie_dict = dict()
        self.case_sensitive = case_sensitive
        self._terms_in_trie = 0

    def __len__(self):
        """Number of terms present in the keyword_trie_dict

        Returns:
            length : int
                Count of number of distinct terms in trie dictionary.

        """
        return self._terms_in_trie

    def __contains__(self, word):
        """To check if word is present in the keyword_trie_dict

        Args:
            word : string
                word that you want to check

        Returns:
            status : bool
                If word is present as it is in keyword_trie_dict then we return True, else False

        Examples:
            >>> keyword_processor.add_keyword('Big Apple')
            >>> 'Big Apple' in keyword_processor
            >>> # True

        """
        # if not self.case_sensitive:
        #     word = word.lower()
        current_dict = self.keyword_trie_dict
        len_covered = 0
        for char in word:
            if char in current_dict:
                current_dict = current_dict[char]
                len_covered += 1
            else:
                break
        return self._keyword in current_dict and len_covered == len(word)

    def __getitem__(self, word):
        """if word is present in keyword_trie_dict return the clean name for it.

        Args:
            word : string
                word that you want to check

        Returns:
            keyword : string
                If word is present as it is in keyword_trie_dict then we return keyword mapped to it.

        Examples:
            >>> keyword_processor.add_keyword('Big Apple', 'New York')
            >>> keyword_processor['Big Apple']
            >>> # New York
        """
        # if not self.case_sensitive:
        #     word = word.lower()
        current_dict = self.keyword_trie_dict
        len_covered = 0
        for char in word:
            if char in current_dict:
                current_dict = current_dict[char]
                len_covered += 1
            else:
                break
        if self._keyword in current_dict and len_covered == len(word):
            return current_dict[self._keyword]

    def __setitem__(self, keyword, clean_name=None):
        """To add keyword to the dictionary
        pass the keyword and the clean name it maps to.

        Args:
            keyword : string
                keyword that you want to identify

            clean_name : string
                clean term for that keyword that you would want to get back in return or replace
                if not provided, keyword will be used as the clean name also.

        Examples:
            >>> keyword_processor['Big Apple'] = 'New York'
        """
        return self._add_keyword_to_trie(keyword, clean_name=clean_name)

    def _add_keyword_to_trie(self, keyword, clean_name=None, case_sensitive=None):
        """
        Internal method to add keyword to trie.
        If case_sensitive is None, uses self.case_sensitive.
        If case_sensitive is False, adds edges for both lower and upper case chars.
        """
        if case_sensitive is None:
            case_sensitive = self.case_sensitive
            
        status = add_keyword_to_trie(self.keyword_trie_dict, keyword, clean_name, case_sensitive, self._keyword)
        if status:
            self._terms_in_trie += 1
        return status

    def __delitem__(self, keyword):
        """To remove keyword from the dictionary
        pass the keyword and the clean name it maps to.

        Args:
            keyword : string
                keyword that you want to remove if it's present

        Examples:
            >>> keyword_processor.add_keyword('Big Apple')
            >>> del keyword_processor['Big Apple']
        """
        status = remove_keyword_from_trie(self.keyword_trie_dict, keyword, self._keyword)
        if status:
            self._terms_in_trie -= 1
        return status

    def __iter__(self):
        """Disabled iteration as get_all_keywords() is the right way to iterate
        """
        raise NotImplementedError("Please use get_all_keywords() instead")

    def set_non_word_boundaries(self, non_word_boundaries):
        """set of characters that will be considered as part of word.

        Args:
            non_word_boundaries (set(str)):
                Set of characters that will be considered as part of word.

        """
        self.non_word_boundaries = non_word_boundaries

    def add_non_word_boundary(self, character):
        """add a character that will be considered as part of word.

        Args:
            character (char):
                Character that will be considered as part of word.

        """
        self.non_word_boundaries.add(character)

    def add_keyword(self, keyword, clean_name=None, case_sensitive=None):
        """To add one or more keywords to the dictionary
        pass the keyword and the clean name it maps to.

        Args:
            keyword : string
                keyword that you want to identify

            clean_name : string
                clean term for that keyword that you would want to get back in return or replace
                if not provided, keyword will be used as the clean name also.
            
            case_sensitive : boolean
                If None, uses the global case_sensitive setting.
                If True, adds the keyword as case-sensitive.
                If False, adds the keyword as case-insensitive.

        Returns:
            status : bool
                The return value. True for success, False otherwise.

        Examples:
            >>> keyword_processor.add_keyword('Big Apple', 'New York')
            >>> # This case 'Big Apple' will return 'New York'
            >>> # OR
            >>> keyword_processor.add_keyword('Big Apple')
            >>> # This case 'Big Apple' will return 'Big Apple'
        """
        return self._add_keyword_to_trie(keyword, clean_name=clean_name, case_sensitive=case_sensitive)

    def remove_keyword(self, keyword):
        """To remove one or more keywords from the dictionary
        pass the keyword and the clean name it maps to.

        Args:
            keyword : string
                keyword that you want to remove if it's present

        Returns:
            status : bool
                The return value. True for success, False otherwise.

        Examples:
            >>> keyword_processor.add_keyword('Big Apple')
            >>> keyword_processor.remove_keyword('Big Apple')
            >>> # Returns True
            >>> # This case 'Big Apple' will no longer be a recognized keyword
            >>> keyword_processor.remove_keyword('Big Apple')
            >>> # Returns False

        """
        return self.__delitem__(keyword)

    def get_keyword(self, word):
        """if word is present in keyword_trie_dict return the clean name for it.

        Args:
            word : string
                word that you want to check

        Returns:
            keyword : string
                If word is present as it is in keyword_trie_dict then we return keyword mapped to it.

        Examples:
            >>> keyword_processor.add_keyword('Big Apple', 'New York')
            >>> keyword_processor.get('Big Apple')
            >>> # New York
        """
        return self.__getitem__(word)

    def add_keyword_from_file(self, keyword_file, encoding="utf-8"):
        """To add keywords from a file

        Args:
            keyword_file : path to keywords file
            encoding : specify the encoding of the file

        Examples:
            keywords file format can be like:

            >>> # Option 1: keywords.txt content
            >>> # java_2e=>java
            >>> # java programing=>java
            >>> # product management=>product management
            >>> # product management techniques=>product management

            >>> # Option 2: keywords.txt content
            >>> # java
            >>> # python
            >>> # c++

            >>> # Option 3: keywords.json content
            >>> # {"java": ["java_2e", "java programing"], "product management": ["PM"]}

            >>> keyword_processor.add_keyword_from_file('keywords.txt')

        Raises:
            IOError: If `keyword_file` path is not valid
        """
        if not os.path.isfile(keyword_file):
            raise IOError("Invalid file path {}".format(keyword_file))

        if keyword_file.endswith(".json"):
            with io.open(keyword_file, encoding=encoding) as f:
                data = json.load(f)
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            # {clean_name: [keywords]}
                            for keyword in value:
                                self.add_keyword(keyword, key)
                        else:
                            # {keyword: clean_name}
                            self.add_keyword(key, value)
                else:
                    raise ValueError("JSON must be a dictionary")
        else:
            with io.open(keyword_file, encoding=encoding) as f:
                for line in f:
                    if '=>' in line:
                        keyword, clean_name = line.split('=>')
                        self.add_keyword(keyword, clean_name.strip())
                    else:
                        keyword = line.strip()
                        if keyword:
                            self.add_keyword(keyword)

    def add_keywords_from_dict(self, keyword_dict):
        """To add keywords from a dictionary

        Args:
            keyword_dict (dict): A dictionary with `str` key and (list `str`) as value

        Examples:
            >>> keyword_dict = {
                    "java": ["java_2e", "java programing"],
                    "product management": ["PM", "product manager"]
                }
            >>> keyword_processor.add_keywords_from_dict(keyword_dict)

        Raises:
            AttributeError: If value for a key in `keyword_dict` is not a list.

        """
        for clean_name, keywords in keyword_dict.items():
            if not isinstance(keywords, list):
                raise AttributeError("Value of key {} should be a list".format(clean_name))

            for keyword in keywords:
                self.add_keyword(keyword, clean_name)



    def remove_keywords_from_dict(self, keyword_dict):
        """To remove keywords from a dictionary

        Args:
            keyword_dict (dict): A dictionary with `str` key and (list `str`) as value

        Examples:
            >>> keyword_dict = {
                    "java": ["java_2e", "java programing"],
                    "product management": ["PM", "product manager"]
                }
            >>> keyword_processor.remove_keywords_from_dict(keyword_dict)

        Raises:
            AttributeError: If value for a key in `keyword_dict` is not a list.

        """
        for clean_name, keywords in keyword_dict.items():
            if not isinstance(keywords, list):
                raise AttributeError("Value of key {} should be a list".format(clean_name))

            for keyword in keywords:
                self.remove_keyword(keyword)

    def add_keywords_from_list(self, keyword_list):
        """To add keywords from a list

        Args:
            keyword_list (list(str)): List of keywords to add

        Examples:
            >>> keyword_processor.add_keywords_from_list(["java", "python"]})
        Raises:
            AttributeError: If `keyword_list` is not a list.

        """
        if not isinstance(keyword_list, list):
            raise AttributeError("keyword_list should be a list")

        for keyword in keyword_list:
            self.add_keyword(keyword)

    def remove_keywords_from_list(self, keyword_list):
        """To remove keywords present in list

        Args:
            keyword_list (list(str)): List of keywords to remove

        Examples:
            >>> keyword_processor.remove_keywords_from_list(["java", "python"]})
        Raises:
            AttributeError: If `keyword_list` is not a list.

        """
        if not isinstance(keyword_list, list):
                raise AttributeError("keyword_list should be a list")

        for keyword in keyword_list:
            self.remove_keyword(keyword)

    def get_all_keywords(self, term_so_far='', current_dict=None):
        """Recursively builds a dictionary of keywords present in the dictionary
        And the clean name mapped to those keywords.

        Args:
            term_so_far : string
                term built so far by adding all previous characters
            current_dict : dict
                current recursive position in dictionary

        Returns:
            terms_present : dict
                A map of key and value where each key is a term in the keyword_trie_dict.
                And value mapped to it is the clean name mapped to it.

        Examples:
            >>> keyword_processor = KeywordProcessor()
            >>> keyword_processor.add_keyword('j2ee', 'Java')
            >>> keyword_processor.add_keyword('Python', 'Python')
            >>> keyword_processor.get_all_keywords()
            >>> {'j2ee': 'Java', 'python': 'Python'}
            >>> # NOTE: for case_insensitive all keys will be lowercased.
        """
        return get_all_keywords(self.keyword_trie_dict, term_so_far, current_dict, self._keyword)

    def extract_keywords(self, sentence, span_info=False, max_cost=0):
        """Searches in the string for all keywords present in corpus.
        Keywords present are added to a list `keywords_extracted` and returned.

        Args:
            sentence (str): Line of text where we will search for keywords
            span_info (bool): True if you need to span the boundaries where the extraction has been performed
            max_cost (int): maximum levensthein distance to accept when extracting keywords

        Returns:
            keywords_extracted (list(str)): List of terms/keywords found in sentence that match our corpus

        Examples:
            >>> from flashtext import KeywordProcessor
            >>> keyword_processor = KeywordProcessor()
            >>> keyword_processor.add_keyword('Big Apple', 'New York')
            >>> keyword_processor.add_keyword('Bay Area')
            >>> keywords_found = keyword_processor.extract_keywords('I love Big Apple and Bay Area.')
            >>> keywords_found
            >>> ['New York', 'Bay Area']
            >>> keywords_found = keyword_processor.extract_keywords('I love Big Aple and Baay Area.', max_cost=1)
            >>> keywords_found
            >>> ['New York', 'Bay Area']
        """
        keywords_extracted = []
        if not sentence:
            # if sentence is empty or none just return empty list
            return keywords_extracted
        # Note: Do NOT convert entire sentence to lowercase here.
        # Unicode chars like Turkish İ change length when lowercased (İ -> i̇).
        # Instead, we lowercase each character individually to preserve span positions.
        
        # Performance: Localize member variables to avoid lookup overhead in loop
        keyword_trie_dict = self.keyword_trie_dict
        keyword_key = self._keyword
        non_word_boundaries = self.non_word_boundaries
        
        current_dict = keyword_trie_dict
        sequence_start_pos = 0
        sequence_end_pos = 0
        reset_current_dict = False
        idx = 0
        sentence_len = len(sentence)
        curr_cost = max_cost
        
        while idx < sentence_len:
            char = sentence[idx]
            # Optimization: We do NOT call lower() here anymore.
            # The Trie contains necessary edges for case-insensitive matching.
            # if not self.case_sensitive:
            #     char = char.lower()
            # when we reach a character that might denote word end
            longest_sequence_found = None
            if char not in non_word_boundaries:

                # if end is present in current_dict
                if keyword_key in current_dict or char in current_dict:
                    # update longest sequence found
                    sequence_found = None
                    is_longer_seq_found = False
                    if keyword_key in current_dict:
                        sequence_found = current_dict[keyword_key]
                        longest_sequence_found = current_dict[keyword_key]
                        sequence_end_pos = idx

                    # re look for longest_sequence from this position
                    if char in current_dict:
                        current_dict_continued = current_dict[char]

                        idy = idx + 1
                        while idy < sentence_len:
                            inner_char = sentence[idy]
                            # if not self.case_sensitive:
                            #     inner_char = inner_char.lower()
                            if keyword_key in current_dict_continued:
                                # Check if we should accept this match:
                                # 1. If next char is a word boundary (not in non_word_boundaries), OR
                                # 2. If last matched char is CJK (not in non_word_boundaries) - CJK doesn't need word boundaries
                                last_matched_char = sentence[idy - 1] if idy > 0 else ''
                                if inner_char not in non_word_boundaries or last_matched_char not in non_word_boundaries:
                                    # update longest sequence found
                                    longest_sequence_found = current_dict_continued[keyword_key]
                                    sequence_end_pos = idy
                                    is_longer_seq_found = True
                            if inner_char in current_dict_continued:
                                current_dict_continued = current_dict_continued[inner_char]
                            elif curr_cost > 0:
                                next_word = self.get_next_word(sentence[idy:])
                                current_dict_continued, cost, _ = next(
                                    self.levensthein(next_word, max_cost=curr_cost, start_node=current_dict_continued),
                                    ({}, 0, 0),
                                ) # current_dict_continued to empty dict by default, so next iteration goes to a `break`
                                curr_cost -= cost
                                idy += len(next_word) - 1
                                if not current_dict_continued:
                                    break
                            else:
                                break
                            idy += 1
                        else:
                            # end of sentence reached.
                            if keyword_key in current_dict_continued:
                                # update longest sequence found
                                longest_sequence_found = current_dict_continued[keyword_key]
                                sequence_end_pos = idy
                                is_longer_seq_found = True
                        if is_longer_seq_found:
                            idx = sequence_end_pos
                    current_dict = keyword_trie_dict
                    if longest_sequence_found:
                        # Optimize: if not span_info, append only keyword
                        if span_info:
                            if isinstance(longest_sequence_found, list):
                                for key in longest_sequence_found:
                                    keywords_extracted.append((key, sequence_start_pos, idx))
                            else:
                                keywords_extracted.append((longest_sequence_found, sequence_start_pos, idx))
                        else:
                            if isinstance(longest_sequence_found, list):
                                for key in longest_sequence_found:
                                    keywords_extracted.append(key)
                            else:
                                keywords_extracted.append(longest_sequence_found)
                                
                        curr_cost = max_cost
                    reset_current_dict = True
                else:
                    # we reset current_dict
                    current_dict = keyword_trie_dict
                    reset_current_dict = True
            elif char in current_dict:
                # we can continue from this char (char is already lowercased if needed)
                current_dict = current_dict[char]
            elif curr_cost > 0:
                next_word = self.get_next_word(sentence[idx:])
                current_dict, cost, _ = next(
                    self.levensthein(next_word, max_cost=curr_cost, start_node=current_dict),
                    (keyword_trie_dict, 0, 0)
                )
                curr_cost -= cost
                idx += len(next_word) - 1
            else:
                # we reset current_dict
                current_dict = keyword_trie_dict
                reset_current_dict = True
                # skip to end of word
                idy = idx + 1
                while idy < sentence_len:
                    skip_char = sentence[idy]
                    # if not self.case_sensitive:
                    #     skip_char = skip_char.lower()
                    if skip_char not in non_word_boundaries:
                        break
                    idy += 1
                # Note: idy points to the first non-boundary char (or end of sentence)
                # After loop ends with idx += 1, we want idx to equal idy
                # So set idx = idy - 1 here
                idx = idy - 1
            # if we are end of sentence and have a sequence discovered
            if idx + 1 >= sentence_len:
                if keyword_key in current_dict:
                    sequence_found = current_dict[keyword_key]
                    if span_info:
                        if isinstance(sequence_found, list):
                            for key in sequence_found:
                                keywords_extracted.append((key, sequence_start_pos, sentence_len))
                        else:
                            keywords_extracted.append((sequence_found, sequence_start_pos, sentence_len))
                    else:
                        if isinstance(sequence_found, list):
                            for key in sequence_found:
                                keywords_extracted.append(key)
                        else:
                            keywords_extracted.append(sequence_found)
            idx += 1
            if reset_current_dict:
                reset_current_dict = False
                # Fix for CJK languages: when a keyword is found, we need to
                # recheck from the end position for adjacent keywords
                if longest_sequence_found:
                    idx -= 1
                sequence_start_pos = idx
        return keywords_extracted

    def replace_keywords(self, sentence, max_cost=0, span_info=False):
        """
        Search for keywords and replace them with the associated name in the
        KeywordProcessor.

        Args:
            sentence (str): Line of text where we will search for keywords
            max_cost (int): Maximum levenshtein distance for fuzzy matching
            span_info (bool): If True, return tuple (new_sentence, list_of_replacements)

        Returns:
            new_sentence (str): Line of text with replaced keywords
            (optional) replacements (list): List of dicts with replacement details

        Examples:
            >>> keyword_processor = KeywordProcessor()
            >>> keyword_processor.add_keyword('Big Apple', 'New York')
            >>> new_sentence = keyword_processor.replace_keywords('I love Big Apple and new york')
            >>> new_sentence
            >>> 'I love New York and New York'

        """
        if not sentence:
            # if sentence is empty or none just return the same.
            if span_info:
                return sentence, []
            return sentence
        
        # Use extract_keywords with span_info to get all matches and their positions
        keywords_with_span = self.extract_keywords(sentence, span_info=True, max_cost=max_cost)
        
        if not keywords_with_span:
            if span_info:
                return sentence, []
            return sentence
        
        # Build new sentence by replacing matched keywords
        new_sentence = []
        last_end = 0
        replacements = []
        
        for keyword, start, end in keywords_with_span:
            if start < last_end:
                 # Skip overlapping keywords (e.g. from multi-label matches)
                 continue
            # Add text before this keyword
            new_sentence.append(sentence[last_end:start])
            # Add the replacement keyword
            new_sentence.append(keyword)
            
            if span_info:
                replacements.append({
                    'original': sentence[start:end],
                    'replacement': keyword,
                    'start': start,
                    'end': end
                })
            
            last_end = end
        
        # Add remaining text after last keyword
        new_sentence.append(sentence[last_end:])
        
        result_sentence = ''.join(new_sentence)
        if span_info:
            return result_sentence, replacements
        return result_sentence

    def extract_sentences(self, text, delimiters=None):
        """
        Extract sentences that contain keywords.
        
        Args:
            text (str): Input text
            delimiters (list of str): Punctuation to split sentences. 
                                      Default: ['.', '?', '!', ';', '\\n']
        Returns:
            list of (str, list): [(sentence, [keywords]), ...]
        """
        return extract_sentences_util(text, self.extract_keywords, delimiters)

    def get_next_word(self, sentence):
        """
        Retrieve the next word in the sequence
        Iterate in the string until finding the first char not in non_word_boundaries

        Args:
            sentence (str): Line of text where we will look for the next word

        Returns:
            next_word (str): The next word in the sentence
        Examples:
            >>> from flashtext import KeywordProcessor
            >>> keyword_processor = KeywordProcessor()
            >>> keyword_processor.add_keyword('Big Apple')
            >>> 'Big'
        """
        next_word = str()
        for char in sentence:
            if char not in self.non_word_boundaries:
                # Check if it's CJK. If so, it's a single-char word/token.
                code = ord(char)
                if (0x4E00 <= code <= 0x9FFF or  # CJK Unified
                    0x3400 <= code <= 0x4DBF or  # CJK Ext A
                    0x3040 <= code <= 0x309F or  # Hiragana
                    0x30A0 <= code <= 0x30FF or  # Katakana
                    0xAC00 <= code <= 0xD7AF):   # Hangul Syllables
                    if not next_word:
                        return char
                    break # If we have "abc", we stop at "機" -> return "abc"
                break
            next_word += char
        return next_word

    def levensthein(self, word, max_cost=2, start_node=None):
        """
        Retrieve the nodes where there is a fuzzy match,
        via levenshtein distance, and with respect to max_cost

        Args:
            word (str): word to find a fuzzy match for
            max_cost (int): maximum levenshtein distance when performing the fuzzy match
            start_node (dict): Trie node from which the search is performed

        Yields:
            node, cost, depth (tuple): A tuple containing the final node,
                                      the cost (i.e the distance), and the depth in the trie

        Examples:
            >>> from flashtext import KeywordProcessor
            >>> keyword_processor = KeywordProcessor(case_sensitive=True)
            >>> keyword_processor.add_keyword('Marie', 'Mary')
            >>> next(keyword_processor.levensthein('Maria', max_cost=1))
            >>> ({'_keyword_': 'Mary'}, 1, 5)
            ...
            >>> keyword_processor = KeywordProcessor(case_sensitive=True
            >>> keyword_processor.add_keyword('Marie Blanc', 'Mary')
            >>> next(keyword_processor.levensthein('Mari', max_cost=1))
            >>> ({' ': {'B': {'l': {'a': {'n': {'c': {'_keyword_': 'Mary'}}}}}}}, 1, 5)
        """
        start_node = start_node or self.keyword_trie_dict
        yield from levensthein(word, max_cost, start_node, self._white_space_chars, self._keyword)

