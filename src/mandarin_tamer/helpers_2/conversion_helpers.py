import time

from .micro_conversion_steps import (
    character_conversion,
    one_to_many_conversion,
    phrase_conversion,
)


def convert_text(sentence, dictionaries, opencc_config, openai_function=None, client=None, debug=False):
    if not debug:
        sentence = phrase_conversion(sentence, dictionaries["phrases"])
        sentence = one_to_many_conversion(sentence, dictionaries["one2many"], opencc_config, openai_function, client)
        return character_conversion(sentence, dictionaries["chars"])
    timings = {}
    s1 = time.perf_counter()
    sentence1 = phrase_conversion(sentence, dictionaries["phrases"])
    timings["phrase_conversion"] = time.perf_counter() - s1
    s2 = time.perf_counter()
    sentence2 = one_to_many_conversion(sentence1, dictionaries["one2many"], opencc_config, openai_function, client)
    timings["one_to_many_conversion"] = time.perf_counter() - s2
    s3 = time.perf_counter()
    sentence3 = character_conversion(sentence2, dictionaries["chars"])
    timings["character_conversion"] = time.perf_counter() - s3
    return sentence3, timings


def apply_conversion_chain(sentence, conversion_functions, debug=False):
    if not debug:
        for major_step in conversion_functions:
            sentence = major_step(sentence)
        return sentence
    timings = {}
    for major_step in conversion_functions:
        result = major_step(sentence)
        # If major_step returns (result, timings), unpack
        if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], dict):
            sentence, minor_timings = result
            timings[major_step.__name__] = minor_timings
        else:
            sentence = result
    # No need to track total_major time
    return sentence, timings
