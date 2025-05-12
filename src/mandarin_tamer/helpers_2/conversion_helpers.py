from .micro_conversion_steps import (
    character_conversion,
    one_to_many_conversion,
    phrase_conversion,
)


def convert_text(sentence, dictionaries, opencc_config, openai_function=None, client=None):
    # Replace phrases first (phrases take precedence over one-to-many mappings)
    sentence = phrase_conversion(sentence, dictionaries["phrases"])

    # Handle ambiguous one-to-many mappings
    sentence = one_to_many_conversion(sentence, dictionaries["one2many"], opencc_config, openai_function, client)

    # Finally, apply direct character replacements
    return character_conversion(sentence, dictionaries["chars"])


def apply_conversion_chain(sentence, conversion_functions, debug=False):
    """
    Apply a series of conversion functions in sequence
    """
    for step in conversion_functions:
        sentence = step(sentence)
        if debug:
            print(f"{sentence} - {step.__name__}")

    return sentence
