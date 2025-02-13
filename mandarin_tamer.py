import sys

sys.path.append("..")
from utils.conversion_config import (
    CONVERSION_CONFIGS,
    SCRIPT_CONVERSION_SEQUENCES,
    SCRIPT_RESET_STEPS,
    ConversionConfig,
)
from utils.conversion_operations import ConversionOperation, DictionaryLoader


class ScriptConverter:
    """Base class for script conversion operations."""

    def __init__(
        self,
        target_script: str,
        include_dicts: dict | None = None,
        exclude_lists: dict | None = None,
        modernize: bool = True,
        normalize: bool = True,
        taiwanize: bool = True,
        improved_one_to_many: bool = False,
    ):
        self.loader = DictionaryLoader()
        self.include_dicts = include_dicts or {}
        self.exclude_lists = exclude_lists or {}
        self.dicts: dict[str, dict] = {}
        self.modernize = modernize
        self.normalize = normalize
        self.taiwanize = taiwanize
        self.target_script = target_script
        self.improved_one_to_many = improved_one_to_many

        # Get the appropriate sequence configuration
        sequence_config = SCRIPT_CONVERSION_SEQUENCES.get(target_script, SCRIPT_CONVERSION_SEQUENCES["simplified"])

        # Build the conversion sequence based on flags
        self.conversion_sequence = [
            step for flag, steps in sequence_config for step in steps if flag is True or getattr(self, str(flag), False)
        ]

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
    ) -> tuple[str, list[tuple[int, int]] | None]:
        """Apply a conversion configuration to a sentence."""
        if config.name not in self.dicts:
            self.load_config(config)

        dicts = self.dicts[config.name]
        new_sentence = sentence

        # Determine if we should reset indexes for script conversion steps
        should_reset_indexes = config.name in SCRIPT_RESET_STEPS and dicts["phrase"] and any(dicts["phrase"].values())
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
                self.improved_one_to_many,
                config.openai_func if self.improved_one_to_many else None,
                config.opencc_config if not self.improved_one_to_many else None,
            )

        # Apply character conversion
        operation = ConversionOperation(new_sentence, phrase_indexes)
        return operation.apply_char_conversion(dicts["char"])

    def convert(self, sentence: str) -> str:
        """Convert text between different Chinese scripts."""
        current_indexes = None
        for config_name in self.conversion_sequence:
            sentence, current_indexes = self.apply_conversion(
                sentence,
                CONVERSION_CONFIGS[config_name],
                current_indexes,
            )
        return sentence


def convert_mandarin_script(
    sentence: str,
    target_script: str = "",
    modernize: bool = True,
    normalize: bool = True,
    taiwanize: bool = True,
    improved_one_to_many: bool = False,
) -> str:
    """Convert text between different Chinese scripts."""
    converter = ScriptConverter(
        target_script=target_script,
        modernize=modernize,
        normalize=normalize,
        taiwanize=taiwanize,
        improved_one_to_many=improved_one_to_many,
    )
    return converter.convert(sentence)
