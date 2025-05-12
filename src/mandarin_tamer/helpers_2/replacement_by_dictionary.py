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
