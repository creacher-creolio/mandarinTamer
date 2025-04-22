import json
from pathlib import Path


def replace_characters_from_string_via_1_to_1_dictionary(sentence: str, one_to_one_dictionary: dict) -> str:
    for char in sentence:
        if char in one_to_one_dictionary:
            sentence = sentence.replace(char, one_to_one_dictionary[char])
    return sentence


def replace_phrases_from_string_via_1_to_1_dictionary(sentence: str, phrase_dictionary: dict) -> str:
    def get_possible_sentence_phrases(sentence, max_phrase_length, sentence_length):
        return sorted(
            [
                sentence[i : i + length]
                for i in range(sentence_length)
                for length in range(1, max_phrase_length + 1)
                if i + length <= sentence_length
            ],
            key=lambda x: (-len(x), x),
        )

    max_phrase_length = 5
    sentence_length = len(sentence)
    possible_sentence_phrases = get_possible_sentence_phrases(sentence, max_phrase_length, sentence_length)
    for phrase in possible_sentence_phrases:
        if phrase in phrase_dictionary:
            sentence = sentence.replace(phrase, phrase_dictionary[phrase])
    return sentence


def replace_characters_via_1_to_1_dictionary(sentence_as_list: list, one_to_one_dictionary: dict) -> list:
    for i, token in enumerate(sentence_as_list):
        for char in token:
            if char in one_to_one_dictionary:
                sentence_as_list[i] = sentence_as_list[i].replace(char, one_to_one_dictionary[char])
    return sentence_as_list


def replace_tokens_via_1_to_1_dictionary(sentence_as_list: list, one_to_one_dictionary: dict) -> list:
    return [one_to_one_dictionary.get(token, token) for token in sentence_as_list]


def json_to_dict(file_path) -> dict:
    with Path(file_path).open() as file:
        return json.load(file)


def tsv_to_dict(file_path, split_func) -> dict:
    with Path(file_path).open() as file:
        return {
            line.split("\t")[0]: split_func(line.split("\t")[1].strip())
            for line in file
            if "\t" in line and len(line.split("\t")) > 1
        }


def tsv_1_to_1_to_dict(file_path) -> dict:
    return tsv_to_dict(file_path, lambda x: x)


def tsv_1_to_many_to_dict(file_path) -> dict:
    return tsv_to_dict(file_path, lambda x: x.split())


def tsv_1_to_first_many_to_dict(file_path) -> dict:
    return tsv_to_dict(file_path, lambda x: x.split()[0])
