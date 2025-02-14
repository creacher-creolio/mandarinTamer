import re
import sys

sys.path.append("..")
from utils.punctuation_utils import punctuation_pattern


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
    def get_phrases_to_skip(sentence: str, dictionary: dict) -> list[str]:
        possible_sentence_phrases = ReplacementUtils.get_possible_sentence_phrases(sentence)
        return ReplacementUtils._get_phrases_to_skip_from_list(possible_sentence_phrases, dictionary)

    @staticmethod
    def get_indexes_to_protect_from_list(
        sentence: str, dictionary: dict, indexes_to_protect: list[tuple[int, int]] | None = None
    ) -> list[tuple[int, int]]:
        indexes_to_protect = indexes_to_protect or []
        for phrase in dictionary:
            start = 0
            while (start := sentence.find(phrase, start)) != -1:
                end = start + len(phrase)
                indexes_to_protect.append((start, end))
                start = end
        for phrase in dictionary.values():
            start = 0
            while (start := sentence.find(phrase, start)) != -1:
                end = start + len(phrase)
                indexes_to_protect.append((start, end))
                start = end

        # Remove duplicates and sort by start index
        return sorted(set(indexes_to_protect), key=lambda x: x[0])

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
        return "".join([dictionary.get(char, char) for char in sentence])

    @staticmethod
    def word_replace_over_string(sentence: str, dictionary: dict) -> str:
        possible_phrases = ReplacementUtils.get_possible_sentence_phrases(sentence)
        for phrase in possible_phrases:
            if phrase in dictionary:
                sentence = sentence.replace(phrase, dictionary[phrase])
        return sentence

    @staticmethod
    def revert_protected_indexes(sentence: str, new_sentence: str, indexes_to_protect: list[tuple[int, int]]) -> str:
        for start, end in indexes_to_protect:
            new_sentence = new_sentence[:start] + sentence[start:end] + new_sentence[end:]
        return new_sentence
