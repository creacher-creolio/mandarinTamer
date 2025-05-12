from .helpers_2.conversion_helpers import apply_conversion_chain, convert_text
from .helpers_2.dictionary_loader import load_conversion_dictionaries
from .helpers_2.open_ai_prompts import (
    initialize_openai_client,
    openai_detaiwanize_one2many_mappings,
    openai_modernize_simp_one2many_mappings,
    openai_modernize_trad_one2many_mappings,
    openai_normalize_simp_one2many_mappings,
    openai_normalize_trad_one2many_mappings,
    openai_s2t_one2many_mappings,
    openai_t2s_one2many_mappings,
    openai_taiwanize_one2many_mappings,
)

# Load dictionaries for each conversion type
simp2simp_modernize = load_conversion_dictionaries("simp2simp", "modern_simp")
trad2trad_modernize = load_conversion_dictionaries("trad2trad", "modern_trad")
simp2simp_normalize = load_conversion_dictionaries("simp2simp", "norm_simp")
trad2trad_normalize = load_conversion_dictionaries("trad2trad", "norm_trad")
simp2trad = load_conversion_dictionaries("simp2trad", "s2t")
trad2simp = load_conversion_dictionaries("trad2simp", "t2s")
trad2tw = load_conversion_dictionaries("tw", "t2tw")
tw2trad = load_conversion_dictionaries("tw", "tw2t")


class MandarinConverter:
    def __init__(self, openai_key=None):
        self.client = initialize_openai_client(openai_key)

    def modernize_simplified(self, sentence):
        return convert_text(sentence, simp2simp_modernize, "s2t", openai_modernize_simp_one2many_mappings, self.client)

    def modernize_traditional(self, sentence):
        return convert_text(sentence, trad2trad_modernize, "t2s", openai_modernize_trad_one2many_mappings, self.client)

    def normalize_simplified(self, sentence):
        return convert_text(sentence, simp2simp_normalize, "s2t", openai_normalize_simp_one2many_mappings, self.client)

    def normalize_traditional(self, sentence):
        return convert_text(sentence, trad2trad_normalize, "t2s", openai_normalize_trad_one2many_mappings, self.client)

    def traditionalize(self, sentence):
        return convert_text(sentence, simp2trad, "s2twp", openai_s2t_one2many_mappings, self.client)

    def simplify(self, sentence):
        return convert_text(sentence, trad2simp, "tw2sp", openai_t2s_one2many_mappings, self.client)

    def taiwanize(self, sentence):
        return convert_text(sentence, trad2tw, "t2tw", openai_taiwanize_one2many_mappings, self.client)

    def detaiwanize(self, sentence):
        return convert_text(sentence, tw2trad, "tw2s", openai_detaiwanize_one2many_mappings, self.client)

    def convert_to_tw_trad(self, sentence, debug=False):
        """Complete conversion pipeline to Taiwan traditional Chinese"""
        steps = [
            self.modernize_simplified,
            self.normalize_simplified,
            self.traditionalize,
            self.modernize_traditional,
            self.normalize_traditional,
            self.taiwanize,
        ]
        return apply_conversion_chain(sentence, steps, debug)

    def convert_to_simp(self, sentence, debug=False):
        """Complete conversion pipeline to simplified Chinese"""
        steps = [
            self.modernize_traditional,
            self.normalize_traditional,
            self.detaiwanize,
            self.simplify,
            self.modernize_simplified,
            self.normalize_simplified,
        ]
        return apply_conversion_chain(sentence, steps, debug)

    def convert_script(self, sentence, target_script="", debug=False):
        """High-level conversion method based on target script"""
        if target_script == "to_tw_trad":
            return self.convert_to_tw_trad(sentence, debug)
        return self.convert_to_simp(sentence, debug)
