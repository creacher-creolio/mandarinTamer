from collections.abc import Callable
from dataclasses import dataclass

from utils.open_ai_prompts import (
    openai_detaiwanize_one2many_mappings,
    openai_modernize_simp_one2many_mappings,
    openai_modernize_trad_one2many_mappings,
    openai_normalize_simp_one2many_mappings,
    openai_normalize_trad_one2many_mappings,
    openai_t2s_one2many_mappings,
)


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


# Script-specific conversion sequences
SCRIPT_CONVERSION_SEQUENCES = {
    "tw_traditional": [
        ("modernize", ["modernize_simp"]),
        ("normalize", ["normalize_simp"]),
        (True, ["simp_to_trad"]),
        ("modernize", ["modernize_trad"]),
        ("normalize", ["normalize_trad"]),
        ("taiwanize", ["taiwanize"]),
    ],
    "simplified": [
        ("modernize", ["modernize_trad"]),
        ("normalize", ["normalize_trad"]),
        (True, ["detaiwanize"]),
        (True, ["trad_to_simp"]),
        ("modernize", ["modernize_simp"]),
        ("normalize", ["normalize_simp"]),
    ],
}

# Script conversion step flags
SCRIPT_RESET_STEPS = ["s2t", "t2s", "t2tw", "tw2t"]
