use pyo3::prelude::*;
use std::collections::{HashMap, HashSet};
use std::cmp::min;
use pyo3::types::{PyDict, PySet, PyList};
use pyo3::exceptions::{PyIOError, PyValueError, PyTypeError};
use std::fs::File;
use std::io::{Read, BufRead, BufReader};

/// Arena-based Trie Node
#[derive(Debug)]
struct TrieNode {
    children: HashMap<char, usize>,
    clean_name: Option<PyObject>, 
}

impl TrieNode {
    fn new() -> Self {
        TrieNode {
            children: HashMap::new(),
            clean_name: None,
        }
    }
}

#[pyclass]
struct KeywordProcessor {
    nodes: Vec<TrieNode>,
    case_sensitive: bool,
    non_word_boundaries: Py<PySet>,
}

#[pymethods]
impl KeywordProcessor {
    #[new]
    #[pyo3(signature = (case_sensitive=false))]
    fn new(py: Python<'_>, case_sensitive: bool) -> Self {
        let non_word_boundaries = PySet::empty(py).unwrap();
        let defaults = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_";
        for c in defaults.chars() {
             let _ = non_word_boundaries.add(c.to_string());
        }
        
        let root = TrieNode::new();
        
        KeywordProcessor {
            nodes: vec![root],
            case_sensitive,
            non_word_boundaries: non_word_boundaries.into(),
        }
    }

    #[pyo3(signature = (keyword, clean_name=None, case_sensitive=None))]
    fn add_keyword(&mut self, py: Python<'_>, keyword: &str, clean_name: Option<PyObject>, case_sensitive: Option<bool>) -> bool {
        let clean_name_obj = match clean_name {
            Some(obj) => obj,
            None => keyword.to_object(py),
        };
        
        // Use override if provided, else global
        let is_case_sensitive = case_sensitive.unwrap_or(self.case_sensitive);

        let mut current_idx = 0;
        let mut added_new = false; 

        for c in keyword.chars() {
            if is_case_sensitive {
                if !self.nodes[current_idx].children.contains_key(&c) {
                    let new_node = TrieNode::new();
                    let new_idx = self.nodes.len();
                    self.nodes.push(new_node);
                    self.nodes[current_idx].children.insert(c, new_idx);
                }
                current_idx = self.nodes[current_idx].children[&c];
            } else {
                let lower = c.to_ascii_lowercase();
                let upper = c.to_ascii_uppercase();

                let existing_idx = self.nodes[current_idx].children.get(&lower)
                    .or_else(|| self.nodes[current_idx].children.get(&upper))
                    .copied();

                let next_idx = match existing_idx {
                    Some(idx) => idx,
                    None => {
                        let new_node = TrieNode::new();
                        let idx = self.nodes.len();
                        self.nodes.push(new_node);
                        idx
                    }
                };

                self.nodes[current_idx].children.insert(lower, next_idx);
                self.nodes[current_idx].children.insert(upper, next_idx);
                
                current_idx = next_idx;
            }
        }

        if self.nodes[current_idx].clean_name.is_none() {
            added_new = true;
        }
        self.nodes[current_idx].clean_name = Some(clean_name_obj);

        added_new
    }
    
    #[pyo3(signature = (file_path, encoding=None))]
    fn add_keyword_from_file(&mut self, py: Python<'_>, file_path: &str, encoding: Option<&str>) -> PyResult<()> {
        let _ = encoding;
        
        // Check for JSON extension
        if file_path.ends_with(".json") {
             let mut file = File::open(file_path).map_err(|e| PyIOError::new_err(e.to_string()))?;
             let mut content = String::new();
             file.read_to_string(&mut content).map_err(|e| PyIOError::new_err(e.to_string()))?;
             
             let json_module = py.import("json")?;
             let dict_obj = json_module.call_method1("loads", (content,))?;
             
             if let Ok(dict) = dict_obj.downcast::<PyDict>() {
                 return self.add_keywords_from_dict(py, dict);
             } else {
                 return Err(PyValueError::new_err("JSON file must contain a dictionary"));
             }
        }
        
        // Text mode
        let file = File::open(file_path).map_err(|e| PyIOError::new_err(e.to_string()))?;
        let reader = BufReader::new(file);
        
        for line_res in reader.lines() {
            if let Ok(line) = line_res {
                if let Some((keyword, clean_name)) = line.split_once("=>") {
                     self.add_keyword(py, keyword.trim(), Some(clean_name.trim().to_object(py)), None);
                } else {
                     self.add_keyword(py, line.trim(), None, None);
                }
            }
        }
        Ok(())
    }
    
    #[pyo3(signature = (keyword))]
    fn remove_keyword(&mut self, keyword: &str) -> bool {
        let mut path = Vec::with_capacity(keyword.len());
        let mut current_idx = 0;
        
        for c in keyword.chars() {
            let next_idx_opt = if self.case_sensitive {
                self.nodes[current_idx].children.get(&c).copied()
            } else {
                let lower = c.to_ascii_lowercase();
                let upper = c.to_ascii_uppercase();
                self.nodes[current_idx].children.get(&lower)
                    .or_else(|| self.nodes[current_idx].children.get(&upper))
                    .copied()
            };

            if let Some(next_idx) = next_idx_opt {
                path.push((current_idx, c));
                current_idx = next_idx;
            } else {
                return false;
            }
        }
        
        if self.nodes[current_idx].clean_name.is_none() {
            return false;
        }
        
        self.nodes[current_idx].clean_name = None;
        let removed_status = true;

        let mut child_idx_to_prune = current_idx;
        
        for (parent_idx, c) in path.into_iter().rev() {
             let child_node = &self.nodes[child_idx_to_prune];
             if child_node.children.is_empty() && child_node.clean_name.is_none() {
                 let parent_node = &mut self.nodes[parent_idx];
                 if self.case_sensitive {
                     parent_node.children.remove(&c);
                 } else {
                     let lower = c.to_ascii_lowercase();
                     let upper = c.to_ascii_uppercase();
                     let remove_lower = parent_node.children.get(&lower).map_or(false, |&i| i == child_idx_to_prune);
                     let remove_upper = parent_node.children.get(&upper).map_or(false, |&i| i == child_idx_to_prune);
                     if remove_lower { parent_node.children.remove(&lower); }
                     if remove_upper { parent_node.children.remove(&upper); }
                 }
                 child_idx_to_prune = parent_idx;
             } else {
                 break;
             }
        }

        removed_status
    }

    #[pyo3(signature = (keyword_list))]
    fn add_keywords_from_list(&mut self, py: Python<'_>, keyword_list: Vec<String>) {
        for keyword in keyword_list {
            self.add_keyword(py, &keyword, None, None);
        }
    }

    #[pyo3(signature = (keyword_dict))]
    fn add_keywords_from_dict(&mut self, py: Python<'_>, keyword_dict: &Bound<'_, PyDict>) -> PyResult<()> {
        for (key, value) in keyword_dict {
            let key_str: String = key.extract()?;
            
            // Check if value is list
            if let Ok(list) = value.extract::<Vec<String>>() {
                // Key is Clean Name, Value is List of Keywords
                let clean_name_obj = key_str.to_object(py);
                for keyword in list {
                    self.add_keyword(py, &keyword, Some(clean_name_obj.clone_ref(py)), None);
                }
            } else if let Ok(val_str) = value.extract::<String>() {
                 // Flat Dictionary: Key is Keyword, Value is Clean Name
                 // This matches typical Python behavior for flat dict
                 self.add_keyword(py, &key_str, Some(val_str.to_object(py)), None);
            } else {
                return Err(pyo3::exceptions::PyAttributeError::new_err(format!("Value of key {} should be a list or string", key_str)));
            }
        }
        Ok(())
    }

    #[pyo3(signature = (keyword_list))]
    fn remove_keywords_from_list(&mut self, keyword_list: Vec<String>) {
        for keyword in keyword_list {
            self.remove_keyword(&keyword);
        }
    }

    #[pyo3(signature = (keyword_dict))]
    fn remove_keywords_from_dict(&mut self, keyword_dict: &Bound<'_, PyDict>) -> PyResult<()> {
        for (key, value) in keyword_dict {
            let key_str: String = key.extract()?;
            
             if let Ok(list) = value.extract::<Vec<String>>() {
                for keyword in list {
                     self.remove_keyword(&keyword);
                }
            } else if let Ok(_val_str) = value.extract::<String>() {
                 // Flat Dict: Key is Keyword
                 self.remove_keyword(&key_str);
            } else {
                return Err(pyo3::exceptions::PyAttributeError::new_err(format!("Value of key {} should be a list or string", key_str)));
            }
        }
        Ok(())
    }
    
    #[pyo3(signature = (sentence, span_info=false, max_cost=0))]
    fn extract_keywords(&self, py: Python<'_>, sentence: &str, span_info: bool, max_cost: usize) -> Vec<PyObject> {
        let mut keywords_extracted = Vec::new();
        if sentence.is_empty() {
            return keywords_extracted;
        }

        let boundary_set: HashSet<char> = self.non_word_boundaries.bind(py).iter()
            .filter_map(|x| x.extract::<String>().ok()) 
            .flat_map(|s| s.chars().collect::<Vec<_>>())
            .collect();

        let chars: Vec<char> = sentence.chars().collect();
        let len = chars.len();
        let mut idx = 0;
        
        while idx < len {
            let mut char_idx = idx;
            let mut current_idx = 0; 
            let mut longest_match: Option<(&PyObject, usize)> = None; 
            let mut curr_cost = max_cost;

            let current_char_is_word_char = boundary_set.contains(&chars[idx]);
            
            if idx > 0 {
                let prev_char = chars[idx - 1];
                let prev_char_is_word_char = boundary_set.contains(&prev_char);
                
                if prev_char_is_word_char && current_char_is_word_char {
                    idx += 1;
                    continue;
                }
            }
            
            while char_idx < len {
                let c = chars[char_idx];
                
                if let Some(&next_idx) = self.nodes[current_idx].children.get(&c) {
                    current_idx = next_idx;
                    if let Some(ref name_obj) = self.nodes[current_idx].clean_name {
                        let is_eof = char_idx + 1 >= len;
                        let last_char_is_boundary = !boundary_set.contains(&c);
                        
                        let is_boundary = if is_eof {
                            true
                        } else {
                            let next_char_is_boundary = !boundary_set.contains(&chars[char_idx + 1]);
                            next_char_is_boundary || last_char_is_boundary
                        };
                        
                        if is_boundary {
                            longest_match = Some((name_obj, char_idx + 1));
                        }
                    }
                    char_idx += 1;
                } else if curr_cost > 0 {
                    let remaining_text: String = chars[char_idx..].iter().collect();
                    let next_word = self.get_next_word_internal(&remaining_text, &boundary_set);
                    
                    if let Some((next_idx, cost, matched_len)) = self.find_fuzzy_node(next_word, current_idx, curr_cost, py) {
                        curr_cost -= cost;
                        current_idx = next_idx;
                        char_idx += matched_len; // matched_len is CHAR COUNT now.
                        
                        if let Some(ref name_obj) = self.nodes[current_idx].clean_name {
                             let is_eof = char_idx >= len; 
                             let last_char = chars[char_idx - 1]; 
                             let last_char_is_boundary = !boundary_set.contains(&last_char); 
                             
                             let is_boundary = if is_eof {
                                 true
                             } else {
                                 let next_char_is_boundary = !boundary_set.contains(&chars[char_idx]);
                                 next_char_is_boundary || last_char_is_boundary
                             };
                             
                             if is_boundary {
                                 longest_match = Some((name_obj, char_idx));
                             }
                        }
                    } else {
                        break;
                    }
                } else {
                    break;
                }
            }
            
            if let Some((name_obj, end_pos)) = longest_match {
                let bound = name_obj.bind(py);
                if bound.is_instance_of::<PyList>() {
                     let list = bound.downcast::<PyList>().unwrap();
                     for item in list.iter() {
                         let item_obj = item.to_object(py);
                         if span_info {
                             let tuple = (item_obj, idx, end_pos);
                             keywords_extracted.push(tuple.to_object(py));
                         } else {
                             keywords_extracted.push(item_obj);
                         }
                     }
                } else {
                     if span_info {
                         let tuple = (name_obj.clone_ref(py), idx, end_pos);
                         keywords_extracted.push(tuple.to_object(py));
                     } else {
                         keywords_extracted.push(name_obj.clone_ref(py));
                     }
                }
                idx = end_pos;
            } else {
                idx += 1;
            }
        }
        
        keywords_extracted
    }
    
    // FIX: Combined Set/String Setter Logic
    #[pyo3(signature = (boundaries))]
    fn set_non_word_boundaries(&mut self, py: Python<'_>, boundaries: &Bound<'_, PyAny>) -> PyResult<()> {
        self._set_non_word_boundaries_logic(py, boundaries)
    }
    
    #[setter(non_word_boundaries)]
    fn set_non_word_boundaries_prop(&mut self, py: Python<'_>, boundaries: &Bound<'_, PyAny>) -> PyResult<()> {
         self._set_non_word_boundaries_logic(py, boundaries)
    }
    
    fn _set_non_word_boundaries_logic(&mut self, py: Python<'_>, boundaries: &Bound<'_, PyAny>) -> PyResult<()> {
         if let Ok(set) = boundaries.downcast::<PySet>() {
             self.non_word_boundaries = set.clone().unbind();
        } else if let Ok(s) = boundaries.extract::<String>() {
             let set = PySet::empty(py)?;
             for c in s.chars() {
                 let _ = set.add(c.to_string());
             }
             self.non_word_boundaries = set.unbind();
        } else {
             return Err(PyTypeError::new_err("Expected set or string"));
        }
        Ok(())
    }
    
    #[pyo3(signature = (text, delimiters=None))]
    fn extract_sentences(&self, py: Python<'_>, text: &str, delimiters: Option<Vec<String>>) -> Vec<(String, Vec<PyObject>)> {
        let mut results = Vec::new();
        if text.is_empty() {
             return results;
        }

        let delims_set: HashSet<char> = match delimiters {
            Some(list) => list.into_iter().flat_map(|s| s.chars().collect::<Vec<_>>()).collect(),
            None => vec!['.', '?', '!', ';', '\n'].into_iter().collect(),
        };

        let mut sentences = Vec::new();
        let mut current_sentence = String::new();
        let chars: Vec<char> = text.chars().collect();
        let len = chars.len();
        let mut i = 0;

        while i < len {
            let c = chars[i];
            current_sentence.push(c);
            
            if delims_set.contains(&c) {
                // Consume consecutive delimiters
                let mut j = i + 1;
                while j < len && delims_set.contains(&chars[j]) {
                     current_sentence.push(chars[j]);
                     j += 1;
                }
                i = j - 1; 
                if !current_sentence.trim().is_empty() {
                    sentences.push(current_sentence.clone());
                }
                current_sentence.clear();
            }
            i += 1;
        }
        if !current_sentence.trim().is_empty() {
            sentences.push(current_sentence);
        }
        
        for sent in sentences {
            let keywords = self.extract_keywords(py, &sent, false, 0);
            if !keywords.is_empty() {
                results.push((sent, keywords));
            }
        }
        
        results
    }
    
    fn __len__(&self) -> usize {
        self.nodes.iter().filter(|n| n.clean_name.is_some()).count()
    }
    
    #[getter]
    fn get_non_word_boundaries(&self, py: Python<'_>) -> Py<PySet> {
        self.non_word_boundaries.clone_ref(py)
    }
    
    #[pyo3(signature = (word, max_cost=2, start_node=None))]
    fn levensthein(
        &self, 
        py: Python<'_>, 
        word: &str, 
        max_cost: usize, 
        start_node: Option<PyObject>
    ) -> PyResult<PyObject> {
        let _ = start_node; 
        
        let rows: Vec<usize> = (0..=word.chars().count()).collect();
        let mut results = Vec::new();
        
        self._levenshtein_rec(py, 0, word, &rows, max_cost, 1, &mut results);
        
        // Return Iterator
        let list = PyList::new(py, results)?;
        // Get Python iterator object
        let iterator = list.call_method0("__iter__")?;
        Ok(iterator.into())
    }
    
    #[pyo3(signature = (text))]
    fn get_next_word(&self, py: Python<'_>, text: &str) -> String {
        let boundary_set: HashSet<char> = self.non_word_boundaries.bind(py).iter()
            .filter_map(|x| x.extract::<String>().ok()) 
            .flat_map(|s| s.chars().collect::<Vec<_>>())
            .collect();
            
        self.get_next_word_internal(text, &boundary_set).to_string()
    }
    
    #[pyo3(signature = (word))]
    fn get_keyword(&self, py: Python<'_>, word: &str) -> Option<PyObject> {
        let mut current_idx = 0;
        for c in word.chars() {
            if let Some(&next_idx) = self.nodes[current_idx].children.get(&c) {
                current_idx = next_idx;
            } else {
                return None;
            }
        }
        self.nodes[current_idx].clean_name.as_ref().map(|o| o.clone_ref(py))
    }
    
    fn __contains__(&self, py: Python<'_>, word: &str) -> bool {
        self.get_keyword(py, word).is_some()
    }
    
    fn __getitem__(&self, py: Python<'_>, word: &str) -> PyResult<PyObject> {
        match self.get_keyword(py, word) {
            Some(name) => Ok(name),
            None => Err(pyo3::exceptions::PyKeyError::new_err(word.to_string())),
        }
    }
    
    fn __setitem__(&mut self, py: Python<'_>, keyword: &str, clean_name: PyObject) {
        self.add_keyword(py, keyword, Some(clean_name), None);
    }
    
    fn __delitem__(&mut self, keyword: &str) -> PyResult<()> {
        if self.remove_keyword(keyword) {
            Ok(())
        } else {
            Err(pyo3::exceptions::PyKeyError::new_err(keyword.to_string()))
        }
    }
    
    fn __iter__(&self) -> PyResult<PyObject> {
        Err(pyo3::exceptions::PyNotImplementedError::new_err("Iteration is disabled, use get_all_keywords()"))
    }

    #[pyo3(signature = ())]
    fn get_all_keywords(&self, py: Python<'_>) -> HashMap<String, PyObject> {
        let mut results = HashMap::new();
        let mut current_prefix = String::new();
        self._get_all_keywords_rec(py, 0, &mut current_prefix, &mut results);
        results
    }
    
    #[pyo3(name = "replace_keywords", signature = (sentence, span_info=false, max_cost=0))]
    fn replace_keywords(&self, py: Python<'_>, sentence: &str, span_info: bool, max_cost: usize) -> PyObject {
        let keywords_found = self.extract_keywords(py, sentence, true, max_cost);
        let mut result = String::with_capacity(sentence.len());
        let mut replacements = Vec::new();
        
        let mut last_end = 0;
        let _ = sentence.len(); 
        
        let char_to_byte_map: Vec<usize> = sentence.char_indices().map(|(i, _)| i).collect();
        let total_chars = char_to_byte_map.len();
        
        for kw_obj in keywords_found {
             let tuple: (PyObject, usize, usize) = kw_obj.extract(py).unwrap();
             let (clean_name, start, end) = tuple;
             
             if start < last_end {
                 continue;
             }
             
             let byte_start_prev = if last_end < total_chars { char_to_byte_map[last_end] } else { sentence.len() };
             let byte_end_prev = if start < total_chars { char_to_byte_map[start] } else { sentence.len() };
             
             result.push_str(&sentence[byte_start_prev..byte_end_prev]);
             
             let clean_str: String = clean_name.extract(py).unwrap_or_else(|_| "".to_string());
             result.push_str(&clean_str);
             
             if span_info {
                 let dict = PyDict::new(py);
                 // original text
                 let byte_start_match = byte_end_prev; 
                 let byte_end_match = if end < total_chars { char_to_byte_map[end] } else { sentence.len() };
                 
                 let original = &sentence[byte_start_match..byte_end_match];
                 
                 let _ = dict.set_item("original", original);
                 let _ = dict.set_item("replacement", clean_str);
                 let _ = dict.set_item("start", start);
                 let _ = dict.set_item("end", end);
                 replacements.push(dict.to_object(py));
             }
             
             last_end = end;
        }
        
        let byte_start_rem = if last_end < total_chars { char_to_byte_map[last_end] } else { sentence.len() };
        result.push_str(&sentence[byte_start_rem..]);
        
        if span_info {
             (result, replacements).to_object(py)
        } else {
             result.to_object(py)
        }
    }
}

impl KeywordProcessor {
    fn _get_all_keywords_rec(&self, py: Python<'_>, node_idx: usize, current_prefix: &mut String, results: &mut HashMap<String, PyObject>) {
        let node = &self.nodes[node_idx];
        
        if let Some(ref clean_name) = node.clean_name {
            results.insert(current_prefix.clone(), clean_name.clone_ref(py));
        }
        
        for (&char_code, &child_idx) in &node.children {
            current_prefix.push(char_code);
            self._get_all_keywords_rec(py, child_idx, current_prefix, results);
            current_prefix.pop(); 
        }
    }

    fn _levenshtein_rec(
        &self, 
        py: Python<'_>,
        node_idx: usize, 
        word: &str, 
        prev_row: &[usize], 
        max_cost: usize, 
        depth: usize,
        results: &mut Vec<(PyObject, usize, usize)>
    ) {
        let node = &self.nodes[node_idx];
        let word_chars: Vec<char> = word.chars().collect();
        let cols = word_chars.len() + 1;

        for (&char_code, &child_idx) in &node.children {
            let mut current_row = vec![0; cols];
            current_row[0] = prev_row[0] + 1;

            let mut min_val = current_row[0];

            for i in 1..cols {
                let insert_cost = current_row[i - 1] + 1;
                let delete_cost = prev_row[i] + 1;
                let replace_cost = if word_chars[i - 1] == char_code {
                    prev_row[i - 1]
                } else {
                    prev_row[i - 1] + 1
                };

                current_row[i] = min(insert_cost, min(delete_cost, replace_cost));
                if current_row[i] < min_val {
                    min_val = current_row[i];
                }
            }

            if current_row[cols - 1] <= max_cost {
                let child_node = &self.nodes[child_idx];
                if let Some(ref clean_name) = child_node.clean_name {
                    let pydict = PyDict::new(py);
                    if pydict.set_item("_keyword_", clean_name).is_ok() {
                        results.push((pydict.into(), current_row[cols - 1], depth));
                    }
                }
            }

            if min_val <= max_cost {
                self._levenshtein_rec(py, child_idx, word, &current_row, max_cost, depth + 1, results);
            }
        }
    }
    
    // INTERNAL helper
    fn get_next_word_internal<'a>(&self, text: &'a str, boundary_set: &HashSet<char>) -> &'a str {
        if text.is_empty() { return ""; }
        
        // CJK check on first char
        let first_char = text.chars().next().unwrap();
        if !boundary_set.contains(&first_char) {
             let code = first_char as u32;
             if (0x4E00 <= code && code <= 0x9FFF) || 
                (0x3400 <= code && code <= 0x4DBF) || 
                (0x3040 <= code && code <= 0x309F) || 
                (0x30A0 <= code && code <= 0x30FF) || 
                (0xAC00 <= code && code <= 0xD7AF) {
                 return &text[..first_char.len_utf8()];
             }
        }
        
        let mut len = 0;
        for c in text.chars() {
             if !boundary_set.contains(&c) {
                 break;
             }
             len += c.len_utf8();
        }
        &text[..len]
    }

    fn find_fuzzy_node(&self, word: &str, start_node_idx: usize, max_cost: usize, _py: Python<'_>) -> Option<(usize, usize, usize)> {
         let rows: Vec<usize> = (0..=word.chars().count()).collect();
         let mut results = Vec::new(); 
         
         self._levenshtein_node_rec(start_node_idx, word, &rows, max_cost, 0, &mut results);
         
         results.into_iter()
            .min_by(|a, b| {
                let cost_cmp = a.1.cmp(&b.1);
                if cost_cmp == std::cmp::Ordering::Equal {
                    b.3.cmp(&a.3) 
                } else {
                    cost_cmp
                }
            })
            .map(|(idx, cost, len, _depth)| (idx, cost, len))
    }
    
    fn _levenshtein_node_rec(
        &self, 
        node_idx: usize, 
        word: &str, 
        prev_row: &[usize], 
        max_cost: usize,
        depth: usize,
        results: &mut Vec<(usize, usize, usize, usize)> 
    ) {
        let node = &self.nodes[node_idx];
        let word_chars: Vec<char> = word.chars().collect();
        let cols = word_chars.len() + 1;

        for (&char_code, &child_idx) in &node.children {
            let mut current_row = vec![0; cols];
            current_row[0] = prev_row[0] + 1;

            let mut min_val = current_row[0];

            for i in 1..cols {
                let insert_cost = current_row[i - 1] + 1;
                let delete_cost = prev_row[i] + 1;
                let replace_cost = if word_chars[i - 1] == char_code {
                    prev_row[i - 1]
                } else {
                    prev_row[i - 1] + 1
                };

                current_row[i] = min(insert_cost, min(delete_cost, replace_cost));
                if current_row[i] < min_val {
                    min_val = current_row[i];
                }
            }

            if current_row[cols - 1] <= max_cost {
                // Returns CHAR count
                let char_len = word.chars().count();
                results.push((child_idx, current_row[cols - 1], char_len, depth + 1));
            }

            if min_val <= max_cost {
                self._levenshtein_node_rec(child_idx, word, &current_row, max_cost, depth + 1, results);
            }
        }
    }

}

#[pyfunction]
fn hello() -> String {
    "hello from rust".to_string()
}

#[pymodule]
fn _core(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello, m)?)?;
    m.add_class::<KeywordProcessor>()?;
    Ok(())
}
