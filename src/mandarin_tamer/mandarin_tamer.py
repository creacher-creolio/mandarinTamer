"""src/mandarinTamer/mandarin_tamer.py - Core script conversion functionality"""

from .helpers.conversion_config import (
    CONVERSION_CONFIGS,
    SCRIPT_RESET_STEPS,
    ConversionConfig,
    get_conversion_steps,
)
from .helpers.conversion_operations import ConversionOperation, DictionaryLoader
from .helpers.replacement_by_dictionary import ReplacementUtils


def convert_mandarin_script(
    sentence: str,
    target_script: str = "zh_cn",
    modernize: bool = True,
    normalize: bool = True,
    taiwanize: bool = True,
    improved_one_to_many: bool = False,
    ner_list: list | None = None,
    include_dicts: dict | None = None,
    exclude_lists: dict | None = None,
) -> str:
    """Convert text between different Chinese scripts."""
    converter = ScriptConverter(
        sentence=sentence,
        target_script=target_script,
        modernize=modernize,
        normalize=normalize,
        taiwanize=taiwanize,
        improved_one_to_many=improved_one_to_many,
        ner_list=ner_list,
        include_dicts=include_dicts,
        exclude_lists=exclude_lists,
    )
    return converter.convert()


class ScriptConverter:
    """Base class for script conversion operations."""

    def __init__(
        self,
        sentence: str,
        target_script: str,
        modernize: bool = True,
        normalize: bool = True,
        taiwanize: bool = True,
        improved_one_to_many: bool = False,
        ner_list: list | None = None,
        include_dicts: dict | None = None,
        exclude_lists: dict | None = None,
    ):
        self.loader = DictionaryLoader()
        self.include_dicts = include_dicts or {}
        self.exclude_lists = exclude_lists or {}
        self.dicts: dict[str, dict] = {}
        self.improved_one_to_many = improved_one_to_many
        self.sentence = sentence

        # Get NER indexes if list provided
        self.ner_indexes = ReplacementUtils.get_ner_indexes(sentence, ner_list) if ner_list else []

        # Get conversion sequence based on flags
        self.conversion_sequence = get_conversion_steps(
            target_script,
            {
                "modernize": modernize,
                "normalize": normalize,
                "taiwanize": taiwanize,
            },
        )

    def convert(self) -> str:
        """Convert text between different Chinese scripts."""
        current_indexes = self.ner_indexes
        sentence = self.sentence
        for config_name in self.conversion_sequence:
            sentence, current_indexes = self.apply_conversion(
                sentence,
                CONVERSION_CONFIGS[config_name],
                current_indexes or [],  # Ensure current_indexes is not None
            )
        return sentence

    def apply_conversion(
        self,
        sentence: str,
        config: ConversionConfig,
        current_indexes: list[tuple[int, int]] | None = None,
    ) -> tuple[str, list[tuple[int, int]] | None]:
        """Apply a conversion configuration to a sentence."""
        if config.name not in self.dicts:
            self.load_config(config)

        dicts = self.dicts[config.name]
        new_sentence = sentence

        # Always include NER indexes in current_indexes
        current_indexes = list(set(current_indexes or []) | set(self.ner_indexes))

        # Determine if we should reset indexes for script conversion steps
        should_reset_indexes = config.name in SCRIPT_RESET_STEPS and dicts["phrase"] and any(dicts["phrase"].values())
        phrase_indexes = self.ner_indexes if should_reset_indexes else current_indexes

        # Apply phrase conversion if dictionary is not empty
        if dicts["phrase"] and any(dicts["phrase"].values()):
            operation = ConversionOperation(new_sentence, phrase_indexes)
            new_sentence, phrase_indexes = operation.apply_phrase_conversion(dicts["phrase"])

        # Apply one-to-many conversion if available
        if dicts["one2many"] and (config.openai_func or config.opencc_config):
            operation = ConversionOperation(new_sentence, phrase_indexes)
            new_sentence = operation.apply_one_to_many_conversion(
                dicts["one2many"],
                self.improved_one_to_many,
                config.openai_func if self.improved_one_to_many else None,
                config.opencc_config if not self.improved_one_to_many else None,
            )

        # Apply character conversion
        operation = ConversionOperation(new_sentence, phrase_indexes)
        return operation.apply_char_conversion(dicts["char"])

    def load_config(self, config: ConversionConfig) -> None:
        """Load dictionaries for a conversion configuration."""
        self.dicts[config.name] = self.loader.load_conversion_config(
            config,
            self.include_dicts,
            self.exclude_lists,
        )
