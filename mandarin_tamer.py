# ruff: noqa: FBT001, FBT002
import sys
from pathlib import Path

from opencc import OpenCC

sys.path.append("..")
from utils.file_conversion import FileConversion
from utils.open_ai_prompts import (
    openai_detaiwanize_one2many_mappings,
    openai_s2t_one2many_mappings,
    openai_t2s_one2many_mappings,
)
from utils.replacement_by_dictionary import ReplacementUtils


class CustomScriptConversionDictionaries:
    def __init__(self, include_dicts=None, exclude_lists=None):
        self.include_dicts = include_dicts or {}
        self.exclude_lists = exclude_lists or {}

        self.modernize_simp_char_dict = self.load_dict("simp2simp", "modern_simp_char.json")
        self.modernize_simp_phrase_dict = self.load_dict("simp2simp", "modern_simp_phrase.json")
        self.normalize_simp_char_dict = self.load_dict("simp2simp", "norm_simp_char.json")
        self.normalize_simp_phrase_dict = self.load_dict("simp2simp", "norm_simp_phrase.json")
        self.modernize_trad_char_dict = self.load_dict("trad2trad", "modern_trad_char.json")
        self.modernize_trad_phrase_dict = self.load_dict("trad2trad", "modern_trad_phrase.json")
        self.normalize_trad_char_dict = self.load_dict("trad2trad", "norm_trad_char.json")
        self.normalize_trad_phrase_dict = self.load_dict("trad2trad", "norm_trad_phrase.json")
        self.s2t_phrases_dict = self.load_dict("simp2trad", "s2t_phrases.json")
        self.trad_phrases = set(self.s2t_phrases_dict.values())
        self.s2t_chars_dict = self.load_dict("simp2trad", "s2t_chars.json")
        self.s2t_one2many_dict = self.load_dict("simp2trad", "s2t_one2many.json")
        self.t2tw_phrases_dict = self.load_dict("tw", "t2tw_phrases.json")
        self.t2tw_chars_dict = self.load_dict("tw", "t2tw_chars.json")
        self.tw2t_phrases_dict = self.load_dict("tw", "tw2t_phrases.json")
        self.tw_phrases = set(self.tw2t_phrases_dict.values())
        self.tw2t_one2many_dict = self.load_dict("tw", "tw2t_one2many.json")
        self.tw2t_chars_dict = self.load_dict("tw", "tw2t_chars.json")
        self.t2s_phrases_dict = self.load_dict("trad2simp", "t2s_phrases.json")
        self.t2s_one2many_dict = self.load_dict("trad2simp", "t2s_one2many.json")
        self.t2s_chars_dict = self.load_dict("trad2simp", "t2s_chars.json")

        self.merged_modern_simp_char_dict = self._merge_dicts(
            self.modernize_simp_char_dict,
            self.include_dicts.get("modern_simplified"),
            self.exclude_lists.get("modern_simplified"),
        )
        self.merged_modern_simp_phrase_dict = self._merge_dicts(
            self.modernize_simp_phrase_dict,
            self.include_dicts.get("modern_simplified"),
            self.exclude_lists.get("modern_simplified"),
        )

        self.merged_norm_simp_char_dict = self._merge_dicts(
            self.normalize_simp_char_dict,
            self.include_dicts.get("norm_simplified"),
            self.exclude_lists.get("norm_simplified"),
        )
        self.merged_norm_simp_phrase_dict = self._merge_dicts(
            self.normalize_simp_phrase_dict,
            self.include_dicts.get("norm_simplified"),
            self.exclude_lists.get("norm_simplified"),
        )

        self.merged_modern_trad_phrase_dict = self._merge_dicts(
            self.modernize_trad_phrase_dict,
            self.include_dicts.get("modern_traditional"),
            self.exclude_lists.get("modern_traditional"),
        )
        self.merged_modern_trad_char_dict = self._merge_dicts(
            self.modernize_trad_char_dict,
            self.include_dicts.get("modern_traditional"),
            self.exclude_lists.get("modern_traditional"),
        )

        self.merged_norm_trad_phrase_dict = self._merge_dicts(
            self.normalize_trad_phrase_dict,
            self.include_dicts.get("norm_traditional"),
            self.exclude_lists.get("norm_traditional"),
        )
        self.merged_norm_trad_char_dict = self._merge_dicts(
            self.normalize_trad_char_dict,
            self.include_dicts.get("norm_traditional"),
            self.exclude_lists.get("norm_traditional"),
        )

        self.merged_s2t_phrases_dict = self._merge_dicts(
            self.s2t_phrases_dict,
            self.include_dicts.get("traditionalize_phrases"),
            self.exclude_lists.get("traditionalize_phrases"),
        )

        self.merged_tw2t_phrases_dict = self._merge_dicts(
            self.tw2t_phrases_dict,
            self.include_dicts.get("detaiwanize_phrases"),
            self.exclude_lists.get("detaiwanize_phrases"),
        )

        self.merged_t2s_one2many_dict = self._merge_dicts(
            self.t2s_one2many_dict,
            self.include_dicts.get("simplify_one_to_many"),
            self.exclude_lists.get("simplify_one_to_many"),
        )

        self.merged_t2s_chars_dict = self._merge_dicts(
            self.t2s_chars_dict,
            self.include_dicts.get("simplify_characters"),
            self.exclude_lists.get("simplify_characters"),
        )

        self.merged_tw2t_chars_dict = self._merge_dicts(
            self.tw2t_chars_dict,
            self.include_dicts.get("detaiwanize_characters"),
            self.exclude_lists.get("detaiwanize_characters"),
        )

    def load_dict(self, sub_dir:str, filename: str) -> dict:
        path = Path(f"../conversion_dictionaries/{sub_dir}/{filename}") if sub_dir else Path(f"../conversion_dictionaries/{filename}")
        return FileConversion.json_to_dict(path)

    def _merge_dicts(
        self,
        base_dict: dict,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> dict:
        merged_dict = base_dict.copy()
        if include_dict:
            merged_dict.update(include_dict)
        if exclude_list:
            for item in exclude_list:
                merged_dict.pop(item, None)
        return merged_dict


class CustomScriptConversion(CustomScriptConversionDictionaries):
    def modernize_simplified(
        self,
        sentence: str,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        # could also try using substring_replace_via_dictionary instead of char_replace_over_string
        phrases_replaced = ReplacementUtils.word_replace_over_string(
            sentence,
            self._merge_dicts(self.modernize_simp_phrase_dict, include_dict, exclude_list),
        )
        return ReplacementUtils.char_replace_over_string(
            phrases_replaced,
            self._merge_dicts(self.modernize_simp_char_dict, include_dict, exclude_list),
        )

    def modernize_simplified_list(
        self,
        sentence: str,
        indexes_to_protect: list[tuple[int, int]],
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        return self._replace_over_list_with_sentence(
            sentence,
            indexes_to_protect,
            self.modernize_simp_char_dict,
            self.modernize_simp_phrase_dict,
            include_dict,
            exclude_list,
        )

    def normalize_simplified(
        self,
        sentence: str,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        phrases_replaced = ReplacementUtils.word_replace_over_string(
            sentence,
            self._merge_dicts(self.merged_norm_simp_char_dict, include_dict, exclude_list),
        )
        return ReplacementUtils.char_replace_over_string(
            phrases_replaced,
            self._merge_dicts(self.merged_norm_simp_phrase_dict, include_dict, exclude_list),
        )

    def normalize_simplified_list(
        self,
        sentence: str,
        indexes_to_protect: list[tuple[int, int]],
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        return self._replace_over_list_with_sentence(
            sentence,
            indexes_to_protect,
            self.normalize_simp_char_dict,
            self.normalize_simp_phrase_dict,
            include_dict,
            exclude_list,
        )

    def modernize_traditional(self, sentence: str) -> str:
        phrases_replaced = ReplacementUtils.word_replace_over_string(sentence, self.merged_modern_trad_phrase_dict)
        return ReplacementUtils.char_replace_over_string(phrases_replaced, self.merged_modern_trad_char_dict)

    def modernize_traditional_list(
        self,
        sentence: str,
        indexes_to_protect: list[tuple[int, int]],
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        return self._replace_over_list_with_sentence(
            sentence,
            indexes_to_protect,
            self.modernize_trad_char_dict,
            self.modernize_trad_phrase_dict,
            include_dict,
            exclude_list,
        )

    def normalize_traditional(
        self,
        sentence: str,
    ) -> str:
        phrases_replaced = ReplacementUtils.word_replace_over_string(sentence, self.merged_norm_trad_phrase_dict)
        return ReplacementUtils.char_replace_over_string(phrases_replaced, self.merged_norm_trad_char_dict)

    def normalize_traditional_list(
        self,
        sentence: str,
        indexes_to_protect: list[tuple[int, int]],
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        return self._replace_over_list_with_sentence(
            sentence,
            indexes_to_protect,
            self.normalize_trad_char_dict,
            self.normalize_trad_phrase_dict,
            include_dict,
            exclude_list,
        )

    def _replace_over_list(  # noqa: PLR0913
        self,
        sentence_parts: list[str],
        phrases_to_skip: list[str],
        char_dict: dict,
        phrase_dict: dict,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> list[str]:
        char_dict = self._merge_dicts(char_dict, include_dict, exclude_list)
        phrase_dict = self._merge_dicts(phrase_dict, include_dict, exclude_list)
        for i, part in enumerate(sentence_parts):
            if part not in phrases_to_skip:
                chars_replaced = ReplacementUtils.char_replace_over_string(part, char_dict)
                sentence_parts[i] = ReplacementUtils.word_replace_over_string(chars_replaced, phrase_dict)
        return sentence_parts

    def _replace_over_list_with_sentence(
        self,
        sentence: str,
        indexes_to_protect: list[tuple[int, int]],
        char_dict: dict,
        phrase_dict: dict,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        char_dict = self._merge_dicts(char_dict, include_dict, exclude_list)
        phrase_dict = self._merge_dicts(phrase_dict, include_dict, exclude_list)
        chars_replaced = ReplacementUtils.char_replace_over_string(sentence, char_dict)
        new_sentence = ReplacementUtils.word_replace_over_string(chars_replaced, phrase_dict)
        return ReplacementUtils.revert_protected_indexes(sentence, new_sentence, indexes_to_protect)

    def map_one_to_many_openai(self, string: str, mapping_dict: dict, openai_function) -> str:
        for char in mapping_dict:
            if char in string:
                string = string.replace(char, openai_function(string, char, mapping_dict))
        return string

    def map_one_to_many_opencc(self, string: str, mapping_dict: dict, opencc_config: str) -> str:
        cc = OpenCC(opencc_config)
        cc_converted_sentence = cc.convert(string)
        for char in mapping_dict:
            if char in string:
                string = string.replace(char, cc_converted_sentence[string.index(char)])
        return string

    def get_converted_opencc_sentence(self, string: str, opencc_config: str) -> str:
        cc = OpenCC(opencc_config)
        return cc.convert(string)

    def _merge_dicts(
        self,
        base_dict: dict,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> dict:
        merged_dict = base_dict.copy()
        if include_dict:
            merged_dict.update(include_dict)
        if exclude_list:
            for item in exclude_list:
                merged_dict.pop(item, None)
        return merged_dict


class ToTwTradScriptConversion(CustomScriptConversion):
    def traditionalize_phrases(
        self,
        sentence: str,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        phrases_dict = self._merge_dicts(self.s2t_phrases_dict, include_dict, exclude_list)
        return ReplacementUtils.word_replace_over_string(sentence, phrases_dict)

    def traditionalize_one_to_many(
        self,
        sentence: str,
        indexes_to_protect: list[tuple[int, int]],
        improved_one_to_many: bool,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        amb_dict = self._merge_dicts(self.s2t_one2many_dict, include_dict, exclude_list)
        chars_in_sentence = [char for char in amb_dict if char in sentence]
        cc_converted_sentence = self.get_converted_opencc_sentence(sentence, "s2twp")
        new_sentence = sentence
        for char in chars_in_sentence:
            if improved_one_to_many:
                new_sentence = self.map_one_to_many_openai(new_sentence, amb_dict, openai_s2t_one2many_mappings)
            else:
                new_sentence = new_sentence.replace(char, cc_converted_sentence[sentence.index(char)])
        return ReplacementUtils.revert_protected_indexes(sentence, new_sentence, indexes_to_protect)

    def traditionalize_characters(
        self,
        sentence: str,
        indexes_to_protect: list[tuple[int, int]],
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        chars_dict = self._merge_dicts(self.s2t_chars_dict, include_dict, exclude_list)
        new_sentence = sentence
        chars_in_sentence = [char for char in chars_dict if char in sentence]
        for char in chars_in_sentence:
            new_sentence = new_sentence.replace(char, chars_dict[char])

        return ReplacementUtils.revert_protected_indexes(sentence, new_sentence, indexes_to_protect)

    def taiwanize_phrases(
        self,
        sentence: str,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> tuple[str, list[tuple[int, int]]]:
        t2tw_phrases_dict = self._merge_dicts(self.t2tw_phrases_dict, include_dict, exclude_list)
        new_sentence = sentence
        possible_sentence_phrases = ReplacementUtils.get_possible_sentence_phrases(sentence)
        for phrase in possible_sentence_phrases:
            if phrase in t2tw_phrases_dict:
                new_sentence = new_sentence.replace(phrase, t2tw_phrases_dict[phrase])
        indexes_to_protect = ReplacementUtils.get_indexes_to_protect_from_list(sentence, t2tw_phrases_dict)
        return new_sentence, indexes_to_protect

    def taiwanize_characters(
        self,
        sentence: str,
        indexes_to_skip: list[tuple[int, int]],
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        chars_dict = self._merge_dicts(self.t2tw_chars_dict, include_dict, exclude_list)
        new_sentence = sentence
        chars_in_sentence = [char for char in chars_dict if char in sentence]
        for char in chars_in_sentence:
            new_sentence = sentence.replace(char, chars_dict[char])
        return ReplacementUtils.revert_protected_indexes(sentence, new_sentence, indexes_to_skip)

    """ Main Sub Function """

    def custom_to_tw_trad(
        self,
        sentence: str,
        improved_one_to_many: bool,
        include_dicts: dict | None = None,
        exclude_lists: dict | None = None,
    ) -> str:
        include_dicts = include_dicts or {}
        exclude_lists = exclude_lists or {}

        sentence = self.modernize_simplified(
            sentence,
            include_dicts.get("modern_simplified"),
            exclude_lists.get("modern_simplified"),
        )
        sentence = self.normalize_simplified(
            sentence,
            include_dicts.get("norm_simplified"),
            exclude_lists.get("norm_simplified"),
        )
        sentence = self.traditionalize_phrases(
            sentence,
            include_dicts.get("traditionalize_phrases"),
            exclude_lists.get("traditionalize_phrases"),
        )

        indexes_to_protect: list[tuple[int, int]] = ReplacementUtils.get_indexes_to_protect_from_list(
            sentence, self.s2t_phrases_dict
        )

        sentence = self.traditionalize_one_to_many(
            sentence,
            indexes_to_protect,
            improved_one_to_many,
            include_dicts.get("traditionalize_one_to_many"),
            exclude_lists.get("traditionalize_one_to_many"),
        )
        sentence = self.traditionalize_characters(
            sentence,
            indexes_to_protect,
            include_dicts.get("traditionalize_characters"),
            exclude_lists.get("traditionalize_characters"),
        )
        sentence = self.modernize_traditional_list(
            sentence,
            indexes_to_protect,
            include_dicts.get("modern_traditional"),
            exclude_lists.get("modern_traditional"),
        )
        sentence = self.normalize_traditional_list(
            sentence,
            indexes_to_protect,
            include_dicts.get("norm_traditional"),
            exclude_lists.get("norm_traditional"),
        )
        sentence, indexes_to_protect = self.taiwanize_phrases(
            sentence,
            include_dicts.get("taiwanize_phrases"),
            exclude_lists.get("taiwanize_phrases"),
        )

        return self.taiwanize_characters(
            sentence,
            indexes_to_protect,
            include_dicts.get("taiwanize_characters"),
            exclude_lists.get("taiwanize_characters"),
        )


class ToSimpScriptConversion(CustomScriptConversion):
    def detaiwanize_phrases(
        self,
        sentence: str,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        phrases_dict = self._merge_dicts(self.tw2t_phrases_dict, include_dict, exclude_list)
        return ReplacementUtils.word_replace_over_string(sentence, phrases_dict)

    def detaiwanize_one_to_many(
        self,
        sentence: str,
        indexes_to_protect: list[tuple[int, int]],
        improved_one_to_many: bool,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        amb_dict = self._merge_dicts(self.tw2t_one2many_dict, include_dict, exclude_list)
        sentence_chars_in_dict = [char for char in amb_dict if char in sentence]
        cc_converted_sentence = self.get_converted_opencc_sentence(sentence, "tw2sp")
        new_sentence = sentence
        for char in sentence_chars_in_dict:
            if improved_one_to_many:
                new_sentence = self.map_one_to_many_openai(
                    new_sentence, amb_dict, openai_detaiwanize_one2many_mappings
                )
            else:
                new_sentence = new_sentence.replace(char, cc_converted_sentence[sentence.index(char)])
        return ReplacementUtils.revert_protected_indexes(sentence, new_sentence, indexes_to_protect)

    def detaiwanize_characters(
        self,
        sentence: str,
        indexes_to_protect: list[tuple[int, int]],
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        chars_dict = self._merge_dicts(self.tw2t_chars_dict, include_dict, exclude_list)
        sentence_chars_in_dict = [char for char in chars_dict if char in sentence]
        new_sentence = sentence
        for char in sentence_chars_in_dict:
            new_sentence = new_sentence.replace(char, chars_dict[char])
        return ReplacementUtils.revert_protected_indexes(sentence, new_sentence, indexes_to_protect)

    def simplify_phrases(
        self,
        sentence: str,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> tuple[str, list[tuple[int, int]]]:
        t2s_phrases_dict = self._merge_dicts(self.t2s_phrases_dict, include_dict, exclude_list)
        new_sentence = sentence
        possible_part_phrases = ReplacementUtils.get_possible_sentence_phrases(sentence)
        for phrase in possible_part_phrases:
            if phrase in t2s_phrases_dict:
                new_sentence = new_sentence.replace(phrase, t2s_phrases_dict[phrase])

        indexes_to_protect = ReplacementUtils.get_indexes_to_protect_from_list(sentence, t2s_phrases_dict)
        return new_sentence, indexes_to_protect

    def simplify_one_to_many(
        self,
        sentence: str,
        indexes_to_protect: list[tuple[int, int]],
        improved_one_to_many: bool,
    ) -> str:
        amb_dict = self.merged_t2s_one2many_dict
        new_sentence = sentence
        if improved_one_to_many:
            new_sentence = self.map_one_to_many_openai(new_sentence, amb_dict, openai_t2s_one2many_mappings)
        else:
            new_sentence = self.map_one_to_many_opencc(new_sentence, amb_dict, "tw2sp")
        return ReplacementUtils.revert_protected_indexes(sentence, new_sentence, indexes_to_protect)

    def simplify_characters(
        self,
        sentence: str,
        indexes_to_protect: list[tuple[int, int]],
    ) -> str:
        chars_dict = self.merged_t2s_chars_dict
        new_sentence = sentence
        sentence_chars_in_dict = [char for char in chars_dict if char in sentence]
        for char in sentence_chars_in_dict:
            new_sentence = new_sentence.replace(char, chars_dict[char])
        return ReplacementUtils.revert_protected_indexes(sentence, new_sentence, indexes_to_protect)

    """ Main Sub Function """

    def custom_to_simp(
        self,
        sentence: str,
        improved_one_to_many: bool,
        include_dicts: dict | None = None,
        exclude_lists: dict | None = None,
    ) -> str:
        include_dicts = include_dicts or {}
        exclude_lists = exclude_lists or {}

        sentence = self.modernize_traditional(sentence)
        sentence = self.normalize_traditional(sentence)
        sentence = self.detaiwanize_phrases(sentence)

        indexes_to_protect: list[tuple[int, int]] = ReplacementUtils.get_indexes_to_protect_from_list(
            sentence, self.tw2t_phrases_dict
        )

        sentence = self.detaiwanize_one_to_many(
            sentence,
            indexes_to_protect,
            improved_one_to_many,
            include_dicts.get("detaiwanize_one_to_many"),
            exclude_lists.get("detaiwanize_one_to_many"),
        )
        sentence = self.detaiwanize_characters(
            sentence,
            indexes_to_protect,
        )
        sentence, indexes_to_protect = self.simplify_phrases(
            sentence,
            include_dicts.get("simplify_phrases"),
            exclude_lists.get("simplify_phrases"),
        )

        sentence = self.simplify_one_to_many(
            sentence,
            indexes_to_protect,
            improved_one_to_many,
        )
        sentence = self.simplify_characters(
            sentence,
            indexes_to_protect,
        )
        sentence = self.modernize_simplified_list(
            sentence,
            indexes_to_protect,
            include_dicts.get("modern_simplified"),
            exclude_lists.get("modern_simplified"),
        )
        return self.normalize_simplified_list(
            sentence,
            indexes_to_protect,
            include_dicts.get("norm_simplified"),
            exclude_lists.get("norm_simplified"),
        )


def custom_script_conversion(
    orig_sentence: str,
    target_script: str = "",
    improved_one_to_many: bool = False,
    include_dicts: dict | None = None,
    exclude_lists: dict | None = None,
) -> str:
    if target_script == "2twtrad":
        return ToTwTradScriptConversion(include_dicts, exclude_lists).custom_to_tw_trad(
            orig_sentence, improved_one_to_many
        )
    return ToSimpScriptConversion(include_dicts, exclude_lists).custom_to_simp(orig_sentence, improved_one_to_many)
