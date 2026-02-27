from typing import *
from dataclasses import dataclass
import unittest
import sys
import string
sys.setrecursionlimit(10**6)

IntList: TypeAlias = Union['ILNode', None]
@dataclass(frozen =True)
class ILNode:
    value: int
    rest: IntList

@dataclass
class WordLines:
    key: str
    value: IntList

WordLinesList: TypeAlias = Optional["WLNode"]
@dataclass(frozen=True)
class WLNode:
    value: WordLines
    rest: WordLinesList

@dataclass
class HashTable:
    bin: List[WordLinesList]
    count: int

# Return the hash code of 's' 
def hash_fn(s: str) -> int:
    h = 0
    for ch in s:
        h = (h * 31 + ord(ch)) 
    return h

# Make a fresh hash table with the given number of bins 'size',
# containing no elements.
def make_hash(size: int) -> HashTable:
    return HashTable([None] * size, 0)

# Return the number of bins in 'ht'.
def hash_size(ht: HashTable) -> int:
    return len(ht.bin)

# Return the number of elements (key-value pairs) in 'ht'.
def hash_count(ht: HashTable) -> int:
    return ht.count

#Helper: returns the WordLines object stored inside a found node.
def _find_wordlines(bin_list: WordLinesList, word: str) -> Optional[WordLines]:
    node = bin_list
    while node is not None:
        if node.value.key == word:
            return node.value
        node = node.rest
    return None
# Return whether 'ht' contains a mapping for the given 'word'.
def has_key(ht: HashTable, word: str) -> bool:
    idx = hash_fn(word) % hash_size(ht)
    return _find_wordlines(ht.bin[idx], word) is not None

#Helper:Converts an intlist to an array[int]
def intlist_to_list(xs: IntList) -> List[int]:
    out: List[int] = []
    while xs is not None:
        out.append(xs.value)
        xs = xs.rest
    return out
# Return the line numbers associated with the key 'word' in 'ht'.
# The returned list should not contain duplicates, but need not be sorted.
def lookup(ht: HashTable, word: str) -> List[int]:
    idx = hash_fn(word) % hash_size(ht)
    wl = _find_wordlines(ht.bin[idx], word)
    if wl is None:
        return []
    return intlist_to_list(wl.value)

#Helper: searches one bin and returns the WordLines object if found.
def find_word(bin_list: WordLinesList, word: str) -> Optional[WordLines]:
    node = bin_list
    while node is not None:
        if node.value.key == word:
            return node.value
        node = node.rest
    return None
# Record in 'ht' that 'word' has an occurrence on line 'line'.
def add(ht: HashTable, word: str, line: int) -> None:
    idx = hash_fn(word) % hash_size(ht)
    
    wl = find_word(ht.bin[idx], word)
    if wl is not None:
        lines = wl.value
        while lines is not None:
            if lines.value == line:
                return 
            lines = lines.rest

        wl.value = ILNode(line, wl.value)
        return

    # Word not found → create new WordLines
    new_pair = WordLines(word, ILNode(line, None))
    ht.bin[idx] = WLNode(new_pair, ht.bin[idx])
    ht.count += 1

# Return the words that have mappings in 'ht'.
# The returned list should not contain duplicates, but need not be sorted.
def hash_keys(ht: HashTable) -> List[str]:
    out: List[str] = []
    for b in ht.bin:
        node = b
        while node is not None:
            out.append(node.value.key)
            node = node.rest
    return out


#helper
def tokenize_line(line: str) -> List[str]:
    line = line.replace("'", "")
    for p in string.punctuation:
        line = line.replace(p, " ")
    line = line.lower()
    tokens = line.split()
    return [t for t in tokens if t.isalpha()]
# Given a hash table 'stop_words' containing stop words as keys, plus
# a sequence of strings 'lines' representing the lines of a document,
# return a hash table representing a concordance of that document.
def make_concordance(stop_words: HashTable, lines: List[str]) -> HashTable:
    ht = make_hash(128)
    for line_no, text in enumerate(lines, start=1):  # blank lines count too
        for w in tokenize_line(text):
            if has_key(stop_words, w):
                continue
            add(ht, w, line_no)
    return ht

# Given an input file path, a stop-words file path, and an output file path,
# overwrite the indicated output file with a sorted concordance of the input file.
def full_concordance(in_file: str, stop_words_file: str, out_file: str) -> None:
    stop_ht = make_hash(128)
    with open(stop_words_file, "r", encoding="utf-8") as f:
        for line in f:
            w = line.strip().lower()
            if w and not has_key(stop_ht, w):
                add(stop_ht, w, 0) 

    with open(in_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print("stop words loaded:", hash_count(stop_ht))
    print("input lines:", len(lines))
    conc = make_concordance(stop_ht, lines)

    words = sorted(hash_keys(conc))
    with open(out_file, "w", encoding="utf-8") as out:
        for w in words:
            nums = lookup(conc, w)
            nums_sorted = sorted(set(nums))
            out.write(f"{w}: " + " ".join(str(n) for n in nums_sorted) + "\n")



class Tests(unittest.TestCase):
    def test_make_hash(self):
        ht = make_hash(5)
        self.assertEqual(hash_count(ht), 0)
        self.assertEqual(ht.bin, [None] * 5)

    def test_hash_size(self):
        ht = make_hash(5)
        self.assertEqual(hash_size(ht), 5)
        self.assertEqual(ht.bin, [None] * 5)

    def test_hash_fn(self):
        self.assertEqual(hash_fn("apple"), hash_fn("apple"))
        self.assertNotEqual(hash_fn("apple"), hash_fn("banana"))

    def test_hash_count(self):
        ht = make_hash(5)
        self.assertEqual(hash_count(ht), 0)
        add(ht, "cat", 1)
        self.assertEqual(hash_count(ht), 1)

    def test_has_key(self):
        ht = make_hash(8)
        self.assertFalse(has_key(ht, "cat"))
        self.assertEqual(lookup(ht, "cat"), [])

    def test_add(self):
        ht = make_hash(8)
        add(ht, "cat", 1)
        add(ht, "cat", 1)  
        add(ht, "cat", 2)

        self.assertEqual(hash_count(ht), 1)
        self.assertEqual(set(lookup(ht, "cat")), {1, 2})
    
    def test_make_concordance(self):
        stop = make_hash(8)
        add(stop, "the", 0)

        lines = [
            "The cat.",
            "Cat dog."
        ]

        conc = make_concordance(stop, lines)

        self.assertFalse(has_key(conc, "the"))
        self.assertEqual(set(lookup(conc, "cat")), {1, 2})
        self.assertEqual(set(lookup(conc, "dog")), {2})

    def test_full_concordance(self):
        full_concordance("sample_input.txt", "stop_words.txt", "sample_output.txt")

        with open("sample_output.txt", "r", encoding="utf-8") as f:
            actual = f.read()

        expected = (
            "cat: 1 3\n"
            "dog: 2 3 4\n"
            "hello: 4\n"
            "however: 4\n"
            "i: 4\n"
            "mat: 1\n"
            "rug: 2 3\n"
            "said: 4\n"
            "sat: 1 2 3\n"
            "together: 3\n"
            "wrong: 4\n")
        self.assertEqual(actual, expected)
        
if (__name__ == '__main__'):
    full_concordance("sample_input.txt", "stop_words.txt", "sample_output.txt")
    unittest.main()
    