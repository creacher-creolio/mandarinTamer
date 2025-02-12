# ruff: noqa: FBT001, FBT002
import sys

sys.path.append("..")
from utils.conversion_operations import ConversionConfig, ConversionOperation, DictionaryLoader
from utils.open_ai_prompts import (
    openai_detaiwanize_one2many_mappings,
    openai_modernize_simp_one2many_mappings,
    openai_modernize_trad_one2many_mappings,
    openai_normalize_simp_one2many_mappings,
    openai_normalize_trad_one2many_mappings,
    openai_t2s_one2many_mappings,
)

# Configuration constants for different conversion types
CONVERSION_CONFIGS = {
    "modernize_simp": ConversionConfig(
        "simp2simp", "modern_simp", openai_modernize_simp_one2many_mappings, "s2twp", "modern_simplified"
    ),
    "normalize_simp": ConversionConfig(
        "simp2simp", "norm_simp", openai_normalize_simp_one2many_mappings, "s2twp", "norm_simplified"
    ),
    "modernize_trad": ConversionConfig(
        "trad2trad", "modern_trad", openai_modernize_trad_one2many_mappings, "s2twp", "modern_traditional"
    ),
    "normalize_trad": ConversionConfig(
        "trad2trad", "norm_trad", openai_normalize_trad_one2many_mappings, "s2twp", "norm_traditional"
    ),
    "simp_to_trad": ConversionConfig("simp2trad", "s2t", openai_t2s_one2many_mappings, "s2twp", "traditionalize"),
    "trad_to_simp": ConversionConfig("trad2simp", "t2s", openai_t2s_one2many_mappings, "tw2sp", "simplify"),
    "detaiwanize": ConversionConfig("tw", "tw2t", openai_detaiwanize_one2many_mappings, "tw2sp", "detaiwanize"),
    "taiwanize": ConversionConfig("tw", "t2tw", None, "s2twp", "taiwanize"),
}


class ScriptConverter:
    """Base class for script conversion operations."""

    def __init__(self, include_dicts: dict | None = None, exclude_lists: dict | None = None):
        self.loader = DictionaryLoader()
        self.include_dicts = include_dicts or {}
        self.exclude_lists = exclude_lists or {}
        self.dicts: dict[str, dict] = {}

    def load_config(self, config: ConversionConfig) -> None:
        """Load dictionaries for a conversion configuration."""
        self.dicts[config.name] = self.loader.load_conversion_config(
            config,
            self.include_dicts,
            self.exclude_lists,
        )

    def apply_conversion(
        self,
        sentence: str,
        config: ConversionConfig,
        indexes_to_protect: list[tuple[int, int]] | None = None,
        improved_one_to_many: bool = False,
    ) -> tuple[str, list[tuple[int, int]] | None]:
        """Apply a conversion configuration to a sentence."""
        if config.name not in self.dicts:
            self.load_config(config)

        dicts = self.dicts[config.name]
        new_sentence = sentence

        # Determine if we should reset indexes for script conversion steps
        should_reset_indexes = (
            config.name in ["s2t", "t2s", "t2tw", "tw2t"] and dicts["phrase"] and any(dicts["phrase"].values())
        )
        phrase_indexes = None if should_reset_indexes else indexes_to_protect

        # Apply phrase conversion if dictionary is not empty
        if dicts["phrase"] and any(dicts["phrase"].values()):
            operation = ConversionOperation(new_sentence, None if should_reset_indexes else phrase_indexes)
            new_sentence, new_indexes = operation.apply_phrase_conversion(dicts["phrase"])
            if should_reset_indexes:
                phrase_indexes = new_indexes

        # Apply one-to-many conversion if available
        if dicts["one2many"] and (config.openai_func or config.opencc_config):
            operation = ConversionOperation(new_sentence, phrase_indexes)
            new_sentence = operation.apply_one_to_many_conversion(
                dicts["one2many"],
                improved_one_to_many,
                config.openai_func if improved_one_to_many else None,
                config.opencc_config if not improved_one_to_many else None,
            )

        # Apply character conversion
        operation = ConversionOperation(new_sentence, phrase_indexes)
        return operation.apply_char_conversion(dicts["char"])

    def convert_sentence(
        self,
        sentence: str,
        conversion_sequence: list[str],
        improved_one_to_many: bool = False,
        include_dicts: dict | None = None,
        exclude_lists: dict | None = None,
    ) -> str:
        """Convert a sentence using a specified conversion sequence."""
        # Initialize with new dictionaries if provided
        if include_dicts or exclude_lists:
            self.include_dicts = include_dicts or {}
            self.exclude_lists = exclude_lists or {}

        # Apply conversion sequence
        current_indexes = None
        for config_name in conversion_sequence:
            sentence, current_indexes = self.apply_conversion(
                sentence,
                CONVERSION_CONFIGS[config_name],
                current_indexes,
                improved_one_to_many=improved_one_to_many,
            )
        return sentence


class ToTwTradConverter(ScriptConverter):
    """Converter for Traditional Taiwanese script."""

    CONVERSION_SEQUENCE = [
        "modernize_simp",
        "normalize_simp",
        "simp_to_trad",
        "modernize_trad",
        "normalize_trad",
        "taiwanize",
    ]

    def convert(
        self,
        sentence: str,
        improved_one_to_many: bool = False,
        include_dicts: dict | None = None,
        exclude_lists: dict | None = None,
    ) -> str:
        """Convert to Traditional Taiwanese script."""
        return self.convert_sentence(
            sentence,
            self.CONVERSION_SEQUENCE,
            improved_one_to_many,
            include_dicts,
            exclude_lists,
        )


class ToSimpConverter(ScriptConverter):
    """Converter for Simplified script."""

    CONVERSION_SEQUENCE = [
        "modernize_trad",
        "normalize_trad",
        "detaiwanize",
        "trad_to_simp",
        "modernize_simp",
        "normalize_simp",
    ]

    def convert(
        self,
        sentence: str,
        improved_one_to_many: bool = False,
        include_dicts: dict | None = None,
        exclude_lists: dict | None = None,
    ) -> str:
        """Convert to Simplified script."""
        return self.convert_sentence(
            sentence,
            self.CONVERSION_SEQUENCE,
            improved_one_to_many,
            include_dicts,
            exclude_lists,
        )


def convert_mandarin_script(
    sentence: str,
    target_script: str = "",
    improved_one_to_many: bool = False,
    include_dicts: dict | None = None,
    exclude_lists: dict | None = None,
) -> str:
    """Convert text between different Chinese scripts."""
    if target_script == "2twtrad":
        return ToTwTradConverter(include_dicts, exclude_lists).convert(sentence, improved_one_to_many)
    return ToSimpConverter(include_dicts, exclude_lists).convert(sentence, improved_one_to_many)
