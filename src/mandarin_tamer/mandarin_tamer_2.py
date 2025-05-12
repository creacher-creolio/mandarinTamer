import sys
from pathlib import Path

from opencc import OpenCC

sys.path.append("..")

from .conversion_dictionaries import DICT_ROOT
from .helpers_2.open_ai_prompts import (
    openai_detaiwanize_one2many_mappings,
    openai_modernize_simp_one2many_mappings,
    openai_modernize_trad_one2many_mappings,
    openai_normalize_simp_one2many_mappings,
    openai_normalize_trad_one2many_mappings,
    openai_s2t_one2many_mappings,
    openai_t2s_one2many_mappings,
    openai_taiwanize_one2many_mappings,
)
from .helpers_2.replacement_by_dictionary import (
    json_to_dict,
    replace_characters_from_string_via_1_to_1_dictionary,
    replace_phrases_from_string_via_1_to_1_dictionary,
)

""" DICTIONARIES """

# MODERNIZATION AND NORMALIZATION
modernize_simp_dict_path = Path(DICT_ROOT) / "simp2simp" / "modern_simp_chars.json"
modernize_trad_dict_path = Path(DICT_ROOT) / "trad2trad" / "modern_trad_chars.json"
normalize_simp_dict_path = Path(DICT_ROOT) / "simp2simp" / "norm_simp_chars.json"
normalize_trad_dict_path = Path(DICT_ROOT) / "trad2trad" / "norm_trad_chars.json"

# Additional paths for phrases and one_to_many dictionaries
modernize_simp_phrases_path = Path(DICT_ROOT) / "simp2simp" / "modern_simp_phrases.json"
modernize_trad_phrases_path = Path(DICT_ROOT) / "trad2trad" / "modern_trad_phrases.json"
normalize_simp_phrases_path = Path(DICT_ROOT) / "simp2simp" / "norm_simp_phrases.json"
normalize_trad_phrases_path = Path(DICT_ROOT) / "trad2trad" / "norm_trad_phrases.json"

modernize_simp_one2many_path = Path(DICT_ROOT) / "simp2simp" / "modern_simp_one2many.json"
modernize_trad_one2many_path = Path(DICT_ROOT) / "trad2trad" / "modern_trad_one2many.json"
normalize_simp_one2many_path = Path(DICT_ROOT) / "simp2simp" / "norm_simp_one2many.json"
normalize_trad_one2many_path = Path(DICT_ROOT) / "trad2trad" / "norm_trad_one2many.json"

# Load dictionaries using json_to_dict
modernize_simp_dict = json_to_dict(modernize_simp_dict_path)
modernize_trad_dict = json_to_dict(modernize_trad_dict_path)
normalize_simp_dict = json_to_dict(normalize_simp_dict_path)
normalize_trad_dict = json_to_dict(normalize_trad_dict_path)

# Load phrase dictionaries
modernize_simp_phrases_dict = json_to_dict(modernize_simp_phrases_path)
modernize_trad_phrases_dict = json_to_dict(modernize_trad_phrases_path)
normalize_simp_phrases_dict = json_to_dict(normalize_simp_phrases_path)
normalize_trad_phrases_dict = json_to_dict(normalize_trad_phrases_path)

# Load one-to-many dictionaries
modernize_simp_amb_dict = json_to_dict(modernize_simp_one2many_path)
modernize_trad_amb_dict = json_to_dict(modernize_trad_one2many_path)
normalize_simp_amb_dict = json_to_dict(normalize_simp_one2many_path)
normalize_trad_amb_dict = json_to_dict(normalize_trad_one2many_path)

# SIMPLIFIED TO TRADITIONAL
s2t_phrases_path = Path(DICT_ROOT) / "simp2trad" / "s2t_phrases.json"
s2t_chars_path = Path(DICT_ROOT) / "simp2trad" / "s2t_chars.json"
s2t_one2many_path = Path(DICT_ROOT) / "simp2trad" / "s2t_one2many.json"

s2t_phrases_dict = json_to_dict(s2t_phrases_path)
s2t_chars_dict = json_to_dict(s2t_chars_path)
s2t_amb_dict = json_to_dict(s2t_one2many_path)

# TAIWANIZATION
t2tw_phrases_path = Path(DICT_ROOT) / "tw" / "t2tw_phrases.json"
t2tw_chars_path = Path(DICT_ROOT) / "tw" / "t2tw_chars.json"
t2tw_one2many_path = Path(DICT_ROOT) / "tw" / "t2tw_one2many.json"

t2tw_phrases_dict = json_to_dict(t2tw_phrases_path)
t2tw_chars_dict = json_to_dict(t2tw_chars_path)
t2tw_amb_dict = json_to_dict(t2tw_one2many_path)

# DETAIWANIZATION
tw2t_phrases_path = Path(DICT_ROOT) / "tw" / "tw2t_phrases.json"
tw2t_one2many_path = Path(DICT_ROOT) / "tw" / "tw2t_one2many.json"
tw2t_chars_path = Path(DICT_ROOT) / "tw" / "tw2t_chars.json"

tw2t_phrases_dict = json_to_dict(tw2t_phrases_path)
tw2t_amb_dict = json_to_dict(tw2t_one2many_path)
tw2t_chars_dict = json_to_dict(tw2t_chars_path)

# TRADITIONAL TO SIMPLIFIED
t2s_phrases_path = Path(DICT_ROOT) / "trad2simp" / "t2s_phrases.json"
t2s_one2many_path = Path(DICT_ROOT) / "trad2simp" / "t2s_one2many.json"
t2s_chars_path = Path(DICT_ROOT) / "trad2simp" / "t2s_chars.json"

t2s_phrases_dict = json_to_dict(t2s_phrases_path)
t2s_amb_dict = json_to_dict(t2s_one2many_path)
t2s_chars_dict = json_to_dict(t2s_chars_path)

""" SHARED """


def map_one_to_many(sentence: str, mapping_dict: dict, opencc_config: str, openai_function, use_ai=False) -> str:
    cc = OpenCC(opencc_config)
    cc_converted_sentence = cc.convert(sentence)

    def char_one2many_opencc(character: str) -> str:
        if character in mapping_dict:
            char_position = sentence.index(character)
            return cc_converted_sentence[char_position]
        return character

    for char in sentence:
        if char in mapping_dict:
            if use_ai:
                sentence = sentence.replace(char, openai_function(char))
            else:
                sentence = sentence.replace(char, char_one2many_opencc(char))
    return sentence


def modernize_simplified(sentence: str) -> str:
    sentence = replace_phrases_from_string_via_1_to_1_dictionary(sentence, modernize_simp_phrases_dict)
    sentence = map_one_to_many(sentence, modernize_simp_amb_dict, "s2s", openai_modernize_simp_one2many_mappings)
    return replace_characters_from_string_via_1_to_1_dictionary(sentence, modernize_simp_dict)


def modernize_traditional(sentence: str) -> str:
    sentence = replace_phrases_from_string_via_1_to_1_dictionary(sentence, modernize_trad_phrases_dict)
    sentence = map_one_to_many(sentence, modernize_trad_amb_dict, "t2t", openai_modernize_trad_one2many_mappings)
    return replace_characters_from_string_via_1_to_1_dictionary(sentence, modernize_trad_dict)


def normalize_simplified(sentence: str) -> str:
    sentence = replace_phrases_from_string_via_1_to_1_dictionary(sentence, normalize_simp_phrases_dict)
    sentence = map_one_to_many(sentence, normalize_simp_amb_dict, "s2s", openai_normalize_simp_one2many_mappings)
    return replace_characters_from_string_via_1_to_1_dictionary(sentence, normalize_simp_dict)


def normalize_traditional(sentence: str) -> str:
    sentence = replace_phrases_from_string_via_1_to_1_dictionary(sentence, normalize_trad_phrases_dict)
    sentence = map_one_to_many(sentence, normalize_trad_amb_dict, "t2t", openai_normalize_trad_one2many_mappings)
    return replace_characters_from_string_via_1_to_1_dictionary(sentence, normalize_trad_dict)


""" SIMPLIFIED TO TRADITIONAL """


def traditionalize(sentence: str) -> str:
    sentence = replace_phrases_from_string_via_1_to_1_dictionary(sentence, s2t_phrases_dict)
    sentence = map_one_to_many(sentence, s2t_amb_dict, "s2twp", openai_s2t_one2many_mappings)
    return replace_characters_from_string_via_1_to_1_dictionary(sentence, s2t_chars_dict)


def taiwanize(sentence: str) -> str:
    sentence = replace_phrases_from_string_via_1_to_1_dictionary(sentence, t2tw_phrases_dict)
    sentence = map_one_to_many(sentence, t2tw_amb_dict, "t2tw", openai_taiwanize_one2many_mappings)
    return replace_characters_from_string_via_1_to_1_dictionary(sentence, t2tw_chars_dict)


def custom_to_tw_trad(sentence: str) -> str:
    steps = [
        modernize_simplified,
        normalize_simplified,
        traditionalize,
        modernize_traditional,
        normalize_traditional,
        taiwanize,
    ]
    for step in steps:
        sentence = step(sentence)
        print(f"{sentence} - {step.__name__}")
    return sentence


""" TRADITIONAL TO SIMPLIFIED """


def detaiwanize(sentence: str) -> str:
    sentence = replace_phrases_from_string_via_1_to_1_dictionary(sentence, tw2t_phrases_dict)
    sentence = map_one_to_many(sentence, tw2t_amb_dict, "tw2t", openai_detaiwanize_one2many_mappings)
    return replace_characters_from_string_via_1_to_1_dictionary(sentence, tw2t_chars_dict)


def simplify(sentence: str) -> str:
    sentence = replace_phrases_from_string_via_1_to_1_dictionary(sentence, t2s_phrases_dict)
    sentence = map_one_to_many(sentence, t2s_amb_dict, "tw2sp", openai_t2s_one2many_mappings)
    return replace_characters_from_string_via_1_to_1_dictionary(sentence, t2s_chars_dict)


def custom_to_simp(sentence: str) -> str:
    steps = [
        modernize_traditional,
        normalize_traditional,
        detaiwanize,
        simplify,
        modernize_simplified,
        normalize_simplified,
    ]
    for step in steps:
        sentence = step(sentence)
        print(f"{sentence} - {step.__name__}")
    return sentence


def custom_transliteration(orig_sentence: str, target_script: str = "") -> str:
    return custom_to_tw_trad(orig_sentence) if target_script == "to_tw_trad" else custom_to_simp(orig_sentence)
