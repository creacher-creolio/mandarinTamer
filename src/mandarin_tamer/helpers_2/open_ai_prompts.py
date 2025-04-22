import json
from openai import OpenAI


client = OpenAI()


def get_openai_response(
    system_content=None, user_content=None, assistant_content=None, json_mode=False, max_tokens=3500, temperature=0
):
    messages = []
    if system_content:
        messages.append({"role": "system", "content": system_content})
    if user_content:
        messages.append({"role": "user", "content": user_content})
    if assistant_content:
        messages.append({"role": "assistant", "content": assistant_content})

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"} if json_mode else {"type": "text"},
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        # top_p=1,
        # frequency_penalty=0,
        # presence_penalty=0,
    )
    return completion.choices[0].message.content


def openai_s2t_ambiguous_mappings(sentence, token, mapping_dict):
    system_context = """
    Return as json the best_replacement_token for the token in the sentence based on the
    simplified_to_traditional_taiwanese_mandarin_character_mapping_dictionary.
    """
    user_context = (
        f"sentence: {sentence}; token: {token}; "
        f"simplified_to_traditional_taiwanese_mandarin_character_mapping_dictionary: {mapping_dict}"
    )
    response = (
        get_openai_response(
            system_content=system_context,
            user_content=user_context,
            json_mode=True,
        )
        or '{"best_replacement_token": ""}'
    )
    json_response = json.loads(response)
    return json_response["best_replacement_token"]


def openai_t2s_ambiguous_mappings(tokenized_sentence, token, mapping_dict):
    system_context = """
    Return as json the best_replacement_token for the token in the tokenized_sentence based on the
    traditional_to_simplified_mandarin_character_mapping_dictionary.
    """
    user_context = (
        f"tokenized_sentence: {tokenized_sentence}; token: {token}; "
        f"traditional_to_simplified_mandarin_character_mapping_dictionary: {mapping_dict}"
    )
    response = (
        get_openai_response(
            system_content=system_context,
            user_content=user_context,
            json_mode=True,
        )
        or '{"best_replacement_token": ""}'
    )
    json_response = json.loads(response)
    return json_response["best_replacement_token"]
