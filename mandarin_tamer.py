# ruff: noqa: FBT001, FBT002
import sys
from pathlib import Path
from opencc import OpenCC


sys.path.append("..")
from utils.file_conversion import FileConversion
from utils.open_ai_prompts import (
    openai_detaiwanize_ambiguous_mappings,
    openai_s2t_ambiguous_mappings,
    openai_t2s_ambiguous_mappings,
)
from utils.replacement_by_dictionary import ReplacementUtils


class CustomTransliterationDictionaries:
    def __init__(self, include_dicts=None, exclude_lists=None):
        self.include_dicts = include_dicts or {}
        self.exclude_lists = exclude_lists or {}

        self.modernize_simp_char_dict = self.load_dict("modernize_simp_char.json")
        self.modernize_simp_phrase_dict = self.load_dict("modernize_simp_phrase.json")
        self.normalize_simp_char_dict = self.load_dict("normalize_simp_char.json")
        self.normalize_simp_phrase_dict = self.load_dict("normalize_simp_phrase.json")
        self.modernize_trad_char_dict = self.load_dict("modernize_trad_char.json")
        self.modernize_trad_phrase_dict = self.load_dict("modernize_trad_phrase.json")
        self.normalize_trad_char_dict = self.load_dict("normalize_trad_char.json")
        self.normalize_trad_phrase_dict = self.load_dict("normalize_trad_phrase.json")
        self.s2t_phrases_dict = self.load_dict("s2t_phrases.json")
        self.trad_phrases = set(self.s2t_phrases_dict.values())
        self.s2t_chars_dict = self.load_dict("s2t_chars.json")
        self.s2t_amb_dict = self.load_dict("s2t_amb.json")
        self.t2tw_phrases_dict = self.load_dict("t2tw_phrases.json")
        self.t2tw_chars_dict = self.load_dict("t2tw_chars.json")
        self.tw2t_phrases_dict = self.load_dict("tw2t_phrases.json")
        self.tw_phrases = set(self.tw2t_phrases_dict.values())
        self.tw2t_amb_dict = self.load_dict("tw2t_amb.json")
        self.tw2t_chars_dict = self.load_dict("tw2t_chars.json")
        self.t2s_phrases_dict = self.load_dict("t2s_phrases.json")
        self.t2s_amb_dict = self.load_dict("t2s_amb.json")
        self.t2s_chars_dict = self.load_dict("t2s_chars.json")

        self.merged_modernize_simp_char_dict = self._merge_dicts(
            self.modernize_simp_char_dict,
            self.include_dicts.get("modernize_simplified"),
            self.exclude_lists.get("modernize_simplified"),
        )
        self.merged_modernize_simp_phrase_dict = self._merge_dicts(
            self.modernize_simp_phrase_dict,
            self.include_dicts.get("modernize_simplified"),
            self.exclude_lists.get("modernize_simplified"),
        )

        self.merged_normalize_simp_char_dict = self._merge_dicts(
            self.normalize_simp_char_dict,
            self.include_dicts.get("normalize_simplified"),
            self.exclude_lists.get("normalize_simplified"),
        )
        self.merged_normalize_simp_phrase_dict = self._merge_dicts(
            self.normalize_simp_phrase_dict,
            self.include_dicts.get("normalize_simplified"),
            self.exclude_lists.get("normalize_simplified"),
        )

        self.merged_modernize_trad_phrase_dict = self._merge_dicts(
            self.modernize_trad_phrase_dict,
            self.include_dicts.get("modernize_traditional"),
            self.exclude_lists.get("modernize_traditional"),
        )
        self.merged_modernize_trad_char_dict = self._merge_dicts(
            self.modernize_trad_char_dict,
            self.include_dicts.get("modernize_traditional"),
            self.exclude_lists.get("modernize_traditional"),
        )

        self.merged_normalize_trad_phrase_dict = self._merge_dicts(
            self.normalize_trad_phrase_dict,
            self.include_dicts.get("normalize_traditional"),
            self.exclude_lists.get("normalize_traditional"),
        )
        self.merged_normalize_trad_char_dict = self._merge_dicts(
            self.normalize_trad_char_dict,
            self.include_dicts.get("normalize_traditional"),
            self.exclude_lists.get("normalize_traditional"),
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

        self.merged_t2s_amb_dict = self._merge_dicts(
            self.t2s_amb_dict,
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

    def load_dict(self, filename: str) -> dict:
        return FileConversion.json_to_dict(
            Path(f"../conversion_dictionaries/{filename}")
        )

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


class CustomTransliteration(CustomTransliterationDictionaries):
    def modernize_simplified(
        self,
        sentence: str,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        # could also try using substring_replace_via_dictionary instead of char_replace_over_string
        phrases_replaced = ReplacementUtils.word_replace_over_string(
            sentence,
            self._merge_dicts(
                self.modernize_simp_phrase_dict, include_dict, exclude_list
            ),
        )
        return ReplacementUtils.char_replace_over_string(
            phrases_replaced,
            self._merge_dicts(
                self.modernize_simp_char_dict, include_dict, exclude_list
            ),
        )

    def modernize_simplified_list(
        self,
        sentence_parts: list[str],
        phrases_to_skip: list[str],
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> list[str]:
        return self._replace_over_list(
            sentence_parts,
            phrases_to_skip,
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
            self._merge_dicts(
                self.merged_normalize_simp_char_dict, include_dict, exclude_list
            ),
        )
        return ReplacementUtils.char_replace_over_string(
            phrases_replaced,
            self._merge_dicts(
                self.merged_normalize_simp_phrase_dict, include_dict, exclude_list
            ),
        )

    def normalize_simplified_list(
        self,
        sentence_parts: list[str],
        phrases_to_skip: list[str],
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> list[str]:
        return self._replace_over_list(
            sentence_parts,
            phrases_to_skip,
            self.normalize_simp_char_dict,
            self.normalize_simp_phrase_dict,
            include_dict,
            exclude_list,
        )

    def modernize_traditional(self, sentence: str) -> str:
        phrases_replaced = ReplacementUtils.word_replace_over_string(
            sentence, self.merged_modernize_trad_phrase_dict
        )
        return ReplacementUtils.char_replace_over_string(
            phrases_replaced, self.merged_modernize_trad_char_dict
        )

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
        phrases_replaced = ReplacementUtils.word_replace_over_string(
            sentence, self.merged_normalize_trad_phrase_dict
        )
        return ReplacementUtils.char_replace_over_string(
            phrases_replaced, self.merged_normalize_trad_char_dict
        )

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
                chars_replaced = ReplacementUtils.char_replace_over_string(
                    part, char_dict
                )
                sentence_parts[i] = ReplacementUtils.word_replace_over_string(
                    chars_replaced, phrase_dict
                )
        return sentence_parts

    def _replace_over_list_with_sentence(
        self,
        sentence: str,
        indexes_to_skip: list[tuple[int, int]],
        char_dict: dict,
        phrase_dict: dict,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        char_dict = self._merge_dicts(char_dict, include_dict, exclude_list)
        phrase_dict = self._merge_dicts(phrase_dict, include_dict, exclude_list)
        chars_replaced = ReplacementUtils.char_replace_over_string(sentence, char_dict)
        new_sentence = ReplacementUtils.word_replace_over_string(
            chars_replaced, phrase_dict
        )
        new_sentence = ReplacementUtils.revert_protected_indexes(
            sentence, new_sentence, indexes_to_skip
        )
        return new_sentence

    def map_one_to_many_openai(
        self, string: str, mapping_dict: dict, openai_function
    ) -> str:
        for char in mapping_dict:
            if char in string:
                string = string.replace(
                    char, openai_function(string, char, mapping_dict)
                )
        return string

    def map_one_to_many_opencc(
        self, string: str, mapping_dict: dict, opencc_config: str
    ) -> str:
        cc = OpenCC(opencc_config)
        cc_converted_sentence = cc.convert(string)
        for char in mapping_dict:
            if char in string:
                string = string.replace(char, cc_converted_sentence[string.index(char)])
        return string

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


class ToTwTradTransliteration(CustomTransliteration):
    def traditionalize_phrases(
        self,
        sentence: str,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        phrases_dict = self._merge_dicts(
            self.s2t_phrases_dict, include_dict, exclude_list
        )
        return ReplacementUtils.word_replace_over_string(sentence, phrases_dict)

    def traditionalize_one_to_many(
        self,
        sentence: str,
        indexes_to_protect: list[tuple[int, int]],
        improved_one_to_many: bool,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        amb_dict = self._merge_dicts(self.s2t_amb_dict, include_dict, exclude_list)
        chars_in_sentence = [char for char in amb_dict if char in sentence]
        cc = OpenCC("s2twp")
        cc_converted_sentence = cc.convert(sentence)
        new_sentence = sentence
        for char in chars_in_sentence:
            if improved_one_to_many:
                sentence = self.map_one_to_many_openai(
                    sentence, amb_dict, openai_s2t_ambiguous_mappings
                )  # TODO: update this to the new format
            else:
                new_sentence = sentence.replace(
                    char, cc_converted_sentence[sentence.index(char)]
                )
        new_sentence = ReplacementUtils.revert_protected_indexes(
            sentence, new_sentence, indexes_to_protect
        )
        return new_sentence

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
            new_sentence = sentence.replace(char, chars_dict[char])

        new_sentence = ReplacementUtils.revert_protected_indexes(
            sentence, new_sentence, indexes_to_protect
        )
        return new_sentence

    def taiwanize_phrases(
        self,
        sentence_parts: list[str],
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> tuple[list[str], list[str]]:
        phrases_to_skip: list[str] = []
        new_sentence_parts: list[str] = []
        t2tw_phrases_dict = self._merge_dicts(
            self.t2tw_phrases_dict, include_dict, exclude_list
        )
        for part in sentence_parts:
            new_part = part
            possible_part_phrases = ReplacementUtils.get_possible_sentence_phrases(part)
            for phrase in possible_part_phrases:
                if phrase in t2tw_phrases_dict:
                    new_part = new_part.replace(phrase, t2tw_phrases_dict[phrase])
                    phrases_to_skip.append(t2tw_phrases_dict[phrase])
            new_sentence_parts.append(new_part)
        return new_sentence_parts, phrases_to_skip

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

        new_sentence = ReplacementUtils.revert_protected_indexes(
            sentence, new_sentence, indexes_to_skip
        )
        return new_sentence

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
            include_dicts.get("modernize_simplified"),
            exclude_lists.get("modernize_simplified"),
        )
        sentence = self.normalize_simplified(
            sentence,
            include_dicts.get("normalize_simplified"),
            exclude_lists.get("normalize_simplified"),
        )
        sentence = self.traditionalize_phrases(
            sentence,
            include_dicts.get("traditionalize_phrases"),
            exclude_lists.get("traditionalize_phrases"),
        )

        indexes_to_protect: list[tuple[int, int]] = (
            ReplacementUtils.get_indexes_to_protect_from_list(
                sentence, self.s2t_phrases_dict
            )
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
            include_dicts.get("modernize_traditional"),
            exclude_lists.get("modernize_traditional"),
        )
        sentence = self.normalize_traditional_list(
            sentence,
            indexes_to_protect,
            include_dicts.get("normalize_traditional"),
            exclude_lists.get("normalize_traditional"),
        )
        t2tw_phrases_dict = self._merge_dicts(
            self.t2tw_phrases_dict,
            include_dicts.get("taiwanize_phrases"),
            exclude_lists.get("taiwanize_phrases"),
        )
        indexes_to_protect: list[tuple[int, int]] = (
            ReplacementUtils.get_indexes_to_protect_from_list(
                sentence, t2tw_phrases_dict
            )
        )
        sentence = self.taiwanize_characters(
            sentence,
            indexes_to_protect,
            include_dicts.get("taiwanize_characters"),
            exclude_lists.get("taiwanize_characters"),
        )
        return sentence


class ToSimpTransliteration(CustomTransliteration):
    def detaiwanize_phrases(
        self,
        sentence: str,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> str:
        phrases_dict = self._merge_dicts(
            self.tw2t_phrases_dict, include_dict, exclude_list
        )
        return ReplacementUtils.word_replace_over_string(sentence, phrases_dict)

    def detaiwanize_one_to_many(
        self,
        sentence_parts: list[str],
        phrases_to_skip: list[str],
        improved_one_to_many: bool,
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> list[str]:
        amb_dict = self._merge_dicts(self.tw2t_amb_dict, include_dict, exclude_list)
        for i, part in enumerate(sentence_parts):
            if part not in phrases_to_skip:
                if improved_one_to_many:
                    sentence_parts[i] = self.map_one_to_many_openai(
                        part, amb_dict, openai_detaiwanize_ambiguous_mappings
                    )
                else:
                    sentence_parts[i] = self.map_one_to_many_opencc(
                        part, amb_dict, "tw2sp"
                    )
        return sentence_parts

    def detaiwanize_characters(
        self,
        sentence_parts: list[str],
        phrases_to_skip: list[str],
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> list[str]:
        chars_dict = self._merge_dicts(self.tw2t_chars_dict, include_dict, exclude_list)
        for i, part in enumerate(sentence_parts):
            if part not in phrases_to_skip:
                for char in part:
                    if char in chars_dict:
                        sentence_parts[i] = sentence_parts[i].replace(
                            char, chars_dict[char]
                        )
        return sentence_parts

    def simplify_phrases(
        self,
        sentence_parts: list[str],
        include_dict: dict | None = None,
        exclude_list: list | None = None,
    ) -> tuple[list[str], list[str]]:
        phrases_to_skip: list[str] = []
        new_sentence_parts: list[str] = []
        t2s_phrases_dict = self._merge_dicts(
            self.t2s_phrases_dict, include_dict, exclude_list
        )
        for part in sentence_parts:
            new_part = part
            possible_part_phrases = ReplacementUtils.get_possible_sentence_phrases(part)
            for phrase in possible_part_phrases:
                if phrase in t2s_phrases_dict:
                    new_part = new_part.replace(phrase, t2s_phrases_dict[phrase])
                    phrases_to_skip.append(t2s_phrases_dict[phrase])
            new_sentence_parts.append(new_part)
        return new_sentence_parts, phrases_to_skip

    def simplify_one_to_many(
        self,
        sentence_parts: list[str],
        phrases_to_skip: list[str],
        improved_one_to_many: bool,
    ) -> list[str]:
        amb_dict = self.merged_t2s_amb_dict
        for i, part in enumerate(sentence_parts):
            if part not in phrases_to_skip:
                if improved_one_to_many:
                    sentence_parts[i] = self.map_one_to_many_openai(
                        part, amb_dict, openai_t2s_ambiguous_mappings
                    )
                else:
                    sentence_parts[i] = self.map_one_to_many_opencc(
                        part, amb_dict, "tw2sp"
                    )
        return sentence_parts

    def simplify_characters(
        self,
        sentence_parts: list[str],
        phrases_to_skip: list[str],
    ) -> list[str]:
        chars_dict = self.merged_t2s_chars_dict
        for i, part in enumerate(sentence_parts):
            if part not in phrases_to_skip:
                for char in chars_dict:
                    if char in part:
                        sentence_parts[i] = sentence_parts[i].replace(
                            char, chars_dict[char]
                        )
        return sentence_parts

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

        phrases_to_skip = ReplacementUtils.get_phrases_to_skip(
            sentence, self.tw2t_phrases_dict
        )
        sentence_parts = ReplacementUtils.split_sentence_by_phrases(
            sentence, phrases_to_skip
        )

        sentence_parts = self.detaiwanize_one_to_many(
            sentence_parts,
            phrases_to_skip,
            improved_one_to_many,
            include_dicts.get("detaiwanize_one_to_many"),
            exclude_lists.get("detaiwanize_one_to_many"),
        )
        sentence_parts = self.detaiwanize_characters(
            sentence_parts,
            phrases_to_skip,
        )
        sentence_parts, phrases_to_skip = self.simplify_phrases(
            sentence_parts,
            include_dicts.get("simplify_phrases"),
            exclude_lists.get("simplify_phrases"),
        )
        sentence_parts = self.simplify_one_to_many(
            sentence_parts,
            phrases_to_skip,
            improved_one_to_many,
        )
        sentence_parts = self.simplify_characters(
            sentence_parts,
            phrases_to_skip,
        )
        sentence_parts = self.modernize_simplified_list(
            sentence_parts,
            phrases_to_skip,
            include_dicts.get("modernize_simplified"),
            exclude_lists.get("modernize_simplified"),
        )
        sentence_parts = self.normalize_simplified_list(
            sentence_parts,
            phrases_to_skip,
            include_dicts.get("normalize_simplified"),
            exclude_lists.get("normalize_simplified"),
        )
        return "".join(sentence_parts)


def custom_transliteration(
    orig_sentence: str,
    target_script: str = "",
    improved_one_to_many: bool = False,
    include_dicts: dict | None = None,
    exclude_lists: dict | None = None,
) -> str:
    if target_script == "2twtrad":
        return ToTwTradTransliteration(include_dicts, exclude_lists).custom_to_tw_trad(
            orig_sentence, improved_one_to_many
        )
    return ToSimpTransliteration(include_dicts, exclude_lists).custom_to_simp(
        orig_sentence, improved_one_to_many
    )
