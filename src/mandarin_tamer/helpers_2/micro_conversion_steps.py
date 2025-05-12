from opencc import OpenCC


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


def phrase_conversion(sentence: str, phrase_dictionary: dict) -> str:
    max_phrase_length = 5
    sentence_length = len(sentence)
    possible_sentence_phrases = get_possible_sentence_phrases(sentence, max_phrase_length, sentence_length)
    for phrase in possible_sentence_phrases:
        if phrase in phrase_dictionary:
            sentence = sentence.replace(phrase, phrase_dictionary[phrase])
    return sentence


def one_to_many_conversion(sentence, mapping_dict, opencc_config, openai_function=None, client=None):
    """
    Handle one-to-many character mappings using either OpenCC or OpenAI
    """
    if not mapping_dict:
        return sentence

    cc = OpenCC(opencc_config)
    cc_converted_sentence = cc.convert(sentence)

    # Create a new string to build the result
    result = list(sentence)

    # Track characters that need conversion
    for i, char in enumerate(sentence):
        if char in mapping_dict:
            if client and openai_function:
                replacement = openai_function(sentence, char, mapping_dict, client)
                result[i] = replacement
            else:
                # Use the corresponding character from OpenCC's conversion at the same position
                result[i] = cc_converted_sentence[i]

    return "".join(result)


def character_conversion(sentence: str, one_to_one_dictionary: dict) -> str:
    for char in sentence:
        if char in one_to_one_dictionary:
            sentence = sentence.replace(char, one_to_one_dictionary[char])
    return sentence
