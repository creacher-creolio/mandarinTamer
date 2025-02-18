from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from opencc import OpenCC

from .conversion_config import ConversionConfig
from .file_conversion import FileConversion
from .replacement_by_dictionary import ReplacementUtils


@dataclass
class ConversionOperation:
    """Base class for conversion operations."""

    sentence: str
    indexes_to_protect: list[tuple[int, int]] | None = None
    include_dict: dict | None = None
    exclude_list: list | None = None

    def __init__(self, sentence: str, indexes_to_protect: list[tuple[int, int]] | None = None):
        self.sentence = sentence
        self.indexes_to_protect = indexes_to_protect or []
        self._phrase_trie = None

    def apply_phrase_conversion(self, phrase_dict: dict) -> tuple[str, list[tuple[int, int]]]:
        """Apply phrase-level conversion."""
        if not phrase_dict or not any(phrase_dict.values()):
            return self.sentence, self.indexes_to_protect or []

        # Build trie once
        if self._phrase_trie is None:
            self._phrase_trie = ReplacementUtils.build_trie_from_dict(phrase_dict)
        # Get all matches
        matches: list[tuple[int, int, str]] = sorted(self._phrase_trie.find_all_matches(self.sentence), reverse=True)

        # Apply replacements from end to start
        result = list(self.sentence)
        new_indexes = set(self.indexes_to_protect or [])

        for start, end, replacement in matches:
            # Check if this range overlaps with protected indexes
            if not any(
                p_start <= start < p_end or p_start < end <= p_end for p_start, p_end in (self.indexes_to_protect or [])
            ):
                result[start:end] = replacement
                new_indexes.add((start, start + len(replacement)))

        return "".join(result), sorted(new_indexes)

    def apply_one_to_many_conversion(
        self,
        mapping_dict: dict,
        use_improved_mode: bool = False,
        openai_func: Callable | None = None,
        opencc_config: str | None = None,
    ) -> str:
        """Apply one-to-many character conversion."""
        if not use_improved_mode and not opencc_config:
            msg = "Either improved mode or opencc_config must be specified"
            raise ValueError(msg)

        new_sentence = self.sentence
        indexes_to_protect = self.indexes_to_protect or []

        if use_improved_mode and openai_func:
            for char in mapping_dict:
                if char in new_sentence:
                    new_sentence = new_sentence.replace(char, openai_func(new_sentence, char, mapping_dict))
        else:
            cc = OpenCC(opencc_config)
            cc_converted = cc.convert(new_sentence)
            for char in mapping_dict:
                if char in new_sentence:
                    new_sentence = new_sentence.replace(char, cc_converted[new_sentence.index(char)])

        return ReplacementUtils.revert_protected_indexes(self.sentence, new_sentence, indexes_to_protect)

    def apply_char_conversion(self, char_dict: dict) -> tuple[str, list[tuple[int, int]] | None]:
        """Apply character-level conversion."""
        chars_in_sentence = [char for char in char_dict if char in self.sentence]
        new_sentence = self.sentence
        indexes_to_protect = self.indexes_to_protect or []

        for char in chars_in_sentence:
            new_sentence = new_sentence.replace(char, char_dict[char])

        final_sentence = ReplacementUtils.revert_protected_indexes(self.sentence, new_sentence, indexes_to_protect)
        return final_sentence, indexes_to_protect


class DictionaryLoader:
    """Handles loading and merging of conversion dictionaries."""

    def __init__(self, base_path: Path | None = None):
        if base_path is None:
            # Use the package's conversion_dictionaries directory
            base_path = Path(__file__).parent.parent / "conversion_dictionaries"
        self.base_path = base_path

    def load_conversion_config(
        self,
        config: ConversionConfig,
        include_dicts: dict | None = None,
        exclude_lists: dict | None = None,
    ) -> dict[str, dict | None]:
        """Load all dictionaries for a conversion configuration."""
        include_dict = include_dicts.get(config.include_key) if include_dicts and config.include_key else None
        exclude_list = exclude_lists.get(config.include_key) if exclude_lists and config.include_key else None

        return {
            "char": self.merge_dicts(
                self.load_dict(config.sub_dir, config.char_file),
                include_dict,
                exclude_list,
            ),
            "phrase": self.merge_dicts(
                self.load_dict(config.sub_dir, config.phrase_file),
                include_dict,
                exclude_list,
            ),
            "one2many": self.merge_dicts(
                self.load_dict(config.sub_dir, config.one2many_file),
                include_dict,
                exclude_list,
            )
            if config.openai_func or config.opencc_config
            else None,
        }

    def merge_dicts(
        self,
        base_dict: dict,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> dict:
        """Merge dictionaries with include/exclude options."""
        merged_dict = base_dict.copy()
        if include_dict:
            merged_dict.update(include_dict)
        if exclude_list:
            for item in exclude_list:
                merged_dict.pop(item, None)
        return merged_dict

    def load_dict(self, sub_dir: str, filename: str) -> dict:
        """Load a dictionary from file."""
        path = self.base_path / sub_dir / filename if sub_dir else self.base_path / filename
        return FileConversion.json_to_dict(path)
