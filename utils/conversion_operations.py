from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from opencc import OpenCC
from utils.file_conversion import FileConversion
from utils.replacement_by_dictionary import ReplacementUtils


@dataclass
class ConversionConfig:
    """Configuration for a specific conversion operation."""

    sub_dir: str
    name: str
    openai_func: Callable | None = None
    opencc_config: str | None = None
    include_key: str | None = None

    @property
    def char_file(self) -> str:
        return f"{self.name}_chars.json"

    @property
    def phrase_file(self) -> str:
        return f"{self.name}_phrases.json"

    @property
    def one2many_file(self) -> str:
        return f"{self.name}_one2many.json"


@dataclass
class ConversionOperation:
    """Base class for conversion operations."""

    sentence: str
    indexes_to_protect: list[tuple[int, int]] | None = None
    include_dict: dict | None = None
    exclude_list: list | None = None

    def apply_phrase_conversion(self, phrase_dict: dict) -> tuple[str, list[tuple[int, int]]]:
        """Apply phrase-level conversion."""
        new_sentence = self.sentence
        indexes_to_protect = []

        # Only process phrases and update indexes if phrase_dict is not empty
        if phrase_dict and any(phrase_dict.values()):
            possible_phrases = ReplacementUtils.get_possible_sentence_phrases(self.sentence)
            for phrase in possible_phrases:
                if phrase in phrase_dict or phrase in phrase_dict.values():
                    new_sentence = new_sentence.replace(phrase, phrase_dict[phrase])
            indexes_to_protect = (
                (ReplacementUtils.get_indexes_to_protect_from_list(self.sentence, phrase_dict) or [])
                if self.indexes_to_protect is None
                else self.indexes_to_protect
            )
        else:
            indexes_to_protect = self.indexes_to_protect or []

        return new_sentence, indexes_to_protect

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

        return (
            ReplacementUtils.revert_protected_indexes(self.sentence, new_sentence, self.indexes_to_protect)
            if self.indexes_to_protect
            else new_sentence
        )

    def apply_char_conversion(self, char_dict: dict) -> tuple[str, list[tuple[int, int]] | None]:
        """Apply character-level conversion."""
        chars_in_sentence = [char for char in char_dict if char in self.sentence]
        new_sentence = self.sentence
        for char in chars_in_sentence:
            new_sentence = new_sentence.replace(char, char_dict[char])

        final_sentence = (
            ReplacementUtils.revert_protected_indexes(self.sentence, new_sentence, self.indexes_to_protect)
            if self.indexes_to_protect
            else new_sentence
        )
        return final_sentence, self.indexes_to_protect


class DictionaryLoader:
    """Handles loading and merging of conversion dictionaries."""

    def __init__(self, base_path: Path = Path("../conversion_dictionaries")):
        self.base_path = base_path

    def load_dict(self, sub_dir: str, filename: str) -> dict:
        """Load a dictionary from file."""
        path = self.base_path / sub_dir / filename if sub_dir else self.base_path / filename
        return FileConversion.json_to_dict(path)

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
