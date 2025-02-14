import re
import sys

sys.path.append("..")
from utils.punctuation_utils import punctuation_pattern
from utils.trie import Trie


class ReplacementUtils:
    @staticmethod
    def get_possible_sentence_phrases(sentence):
        sentence = "".join([char for char in sentence if char not in punctuation_pattern])
        sentence_length = len(sentence)
        max_phrase_length = 5
        return sorted(
            [
                sentence[i : i + length]
                for i in range(sentence_length)
                for length in range(2, max_phrase_length + 1)
                if i + length <= sentence_length
            ],
            key=lambda x: (-len(x), x),
        )

    @staticmethod
    def build_trie_from_dict(dictionary: dict) -> Trie:
        trie = Trie()
        for key, value in dictionary.items():
            trie.insert(key, value)
        return trie

    @staticmethod
    def get_phrases_to_skip(sentence: str, dictionary: dict) -> list[str]:
        # Build trie once and cache it
        trie = ReplacementUtils.build_trie_from_dict(dictionary)
        matches = trie.find_all_matches(sentence)
        return list({match[2] for match in matches})  # Using set for unique values

    @staticmethod
    def get_indexes_to_protect_from_list(
        sentence: str, dictionary: dict, indexes_to_protect: list[tuple[int, int]] | None = None
    ) -> list[tuple[int, int]]:
        indexes_to_protect = set(indexes_to_protect or [])

        # Build tries for both forward and reverse lookups
        forward_trie = ReplacementUtils.build_trie_from_dict(dictionary)
        reverse_dict = {v: k for k, v in dictionary.items()}
        reverse_trie = ReplacementUtils.build_trie_from_dict(reverse_dict)

        # Get matches from both tries
        forward_matches = forward_trie.find_all_matches(sentence)
        reverse_matches = reverse_trie.find_all_matches(sentence)

        # Add all matches to protected indexes
        for start, end, _ in forward_matches + reverse_matches:
            indexes_to_protect.add((start, end))

        return sorted(indexes_to_protect)

    @staticmethod
    def get_ner_indexes(sentence: str, ner_list: list) -> list[tuple[int, int]]:
        """Get indexes of named entities that should be protected from conversion."""
        indexes_to_protect = []
        for entity in ner_list:
            start = 0
            while (start := sentence.find(entity, start)) != -1:
                end = start + len(entity)
                indexes_to_protect.append((start, end))
                start = end
        return sorted(set(indexes_to_protect), key=lambda x: x[0])

    @staticmethod
    def _get_phrases_to_skip_from_list(phrases: list[str], dictionary: dict) -> list[str]:
        phrases_to_skip = []
        for phrase in phrases:
            if phrase in dictionary:
                phrases_to_skip.append(dictionary[phrase])
            if phrase in dictionary.values():
                phrases_to_skip.append(phrase)
        return phrases_to_skip

    @staticmethod
    def split_sentence_by_phrases(sentence: str, phrases: list[str]) -> list[str]:
        if not phrases:
            return [sentence]
        # Sort phrases by length (longest first) to ensure longer phrases are matched first
        sorted_phrases = sorted(phrases, key=len, reverse=True)
        # Escape special regex characters in phrases
        escaped_phrases = [re.escape(phrase) for phrase in sorted_phrases]
        # Create a regex pattern to match any of the phrases
        pattern = f"({'|'.join(escaped_phrases)})"
        # Split the sentence by matching the phrases
        parts = re.split(pattern, sentence)
        # Filter out any empty strings that might result from splitting
        return [part for part in parts if part]

    @staticmethod
    def substring_replace_via_dictionary(sentence: str, dictionary: dict) -> str:
        for k, v in dictionary.items():
            if k in sentence:
                sentence = sentence.replace(k, v)
        return sentence

    @staticmethod
    def char_replace_over_string(sentence: str, dictionary: dict) -> str:
        # Pre-build translation table for faster character replacement
        trans_table = str.maketrans(dictionary)
        return sentence.translate(trans_table)

    @staticmethod
    def word_replace_over_string(sentence: str, dictionary: dict) -> str:
        trie = ReplacementUtils.build_trie_from_dict(dictionary)
        matches = sorted(trie.find_all_matches(sentence), reverse=True)

        # Apply replacements from end to start to avoid index issues
        result = list(sentence)
        for start, end, replacement in matches:
            result[start:end] = replacement

        return "".join(result)

    @staticmethod
    def revert_protected_indexes(sentence: str, new_sentence: str, indexes_to_protect: list[tuple[int, int]]) -> str:
        for start, end in indexes_to_protect:
            new_sentence = new_sentence[:start] + sentence[start:end] + new_sentence[end:]
        return new_sentence
