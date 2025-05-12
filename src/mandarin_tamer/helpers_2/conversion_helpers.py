from opencc import OpenCC

from .replacement_by_dictionary import (
    replace_characters_from_string_via_1_to_1_dictionary,
    replace_phrases_from_string_via_1_to_1_dictionary,
)


def map_one_to_many(sentence, mapping_dict, opencc_config, openai_function=None, client=None):
    """
    Handle one-to-many character mappings using either OpenCC or OpenAI
    """
    if not mapping_dict:
        return sentence

    cc = OpenCC(opencc_config)
    cc_converted_sentence = cc.convert(sentence)

    def char_one2many_opencc(character):
        if character in mapping_dict:
            char_position = sentence.index(character)
            return cc_converted_sentence[char_position]
        return character

    for char in sentence:
        if char in mapping_dict:
            if client and openai_function:
                replacement = openai_function(sentence, char, mapping_dict, client)
                sentence = sentence.replace(char, replacement)
            else:
                sentence = sentence.replace(char, char_one2many_opencc(char))

    return sentence


def convert_text(sentence, dictionaries, opencc_config, openai_function=None, client=None):
    """
    Apply complete text conversion process with phrases, one-to-many characters, and individual characters
    """
    # Replace phrases first (longer patterns take precedence)
    sentence = replace_phrases_from_string_via_1_to_1_dictionary(sentence, dictionaries["phrases"])

    # Handle ambiguous one-to-many mappings
    sentence = map_one_to_many(sentence, dictionaries["one2many"], opencc_config, openai_function, client)

    # Finally, apply direct character replacements
    return replace_characters_from_string_via_1_to_1_dictionary(sentence, dictionaries["chars"])


def apply_conversion_chain(sentence, conversion_functions, debug=False):
    """
    Apply a series of conversion functions in sequence
    """
    for step in conversion_functions:
        sentence = step(sentence)
        if debug:
            print(f"{sentence} - {step.__name__}")

    return sentence
