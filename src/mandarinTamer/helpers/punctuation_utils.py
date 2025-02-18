punctuation_misc = "—"
punctuation_english = "!#$%&'\"()*+,-./:;<=>?@[\\]^_`{|}~"
punctuation_spanish = "¡¿«»"
punctuation_chinese = "。，、…《》·：？！；“”‘’（）…"
number_pattern = "0123456789"

punctuation_pattern = (
    punctuation_misc + punctuation_english + punctuation_spanish + punctuation_chinese + number_pattern
)
punctuation_list = list(punctuation_pattern)
punctuation_repetitions = ("..", "...", "……", "!!", "!!!", "??", "???", "--", "__")
punctuation_list.extend(punctuation_repetitions)
