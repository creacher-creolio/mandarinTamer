import json
from pathlib import Path

from ..conversion_dictionaries import DICT_ROOT


def json_to_dict(file_path):
    """Load a JSON file into a dictionary"""
    with Path(file_path).open() as file:
        return json.load(file)


def load_dictionary(subpath, filename):
    """Load a dictionary from the specified subpath and filename"""
    path = Path(DICT_ROOT) / subpath / filename
    return json_to_dict(path)


def load_conversion_dictionaries(script_type, variant):
    """Load all dictionaries for a specific script conversion type and variant"""
    # Valid script types are: simp2simp, trad2trad, simp2trad, trad2simp, tw
    return {
        "chars": load_dictionary(script_type, f"{variant}_chars.json"),
        "phrases": load_dictionary(script_type, f"{variant}_phrases.json"),
        "one2many": load_dictionary(script_type, f"{variant}_one2many.json"),
    }
