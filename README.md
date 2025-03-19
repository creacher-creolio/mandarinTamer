# MandarinTamer

MandarinTamer is a Python library for converting Mandarin text between Simplified Chinese and Traditional Chinese, with a focus on the Taiwanese variant. It's designed to be accurate, flexible, and easy to use.

## What Makes MandarinTamer Unique?

MandarinTamer stands out for its ability to convert text without requiring prior knowledge of the input script. It seamlessly handles Simplified, all forms of Traditional, or even mixed-script text, automatically transforming it into your desired script.

## Key Features

- **Simplified ↔ Taiwanese Traditional Conversion**: Handle text transformation with precision, adhering to regional linguistic norms.
- **AI-Powered Context Awareness**: Uses sentence context with AI to intelligently resolve one-to-many mappings.
- **Context-Free Accuracy**: Achieves high accuracy without requiring metadata or prior knowledge of the input text.
- **Modernization and Normalization**: Optionally replace rare or archaic words with more common used equivalents.
- **Open Source**: Built for developers and researchers to adapt, enhance, and integrate into other projects.

## Why MandarinTamer?

Traditional conversion tools often fail to capture the nuances of regional variants like Taiwanese Traditional Chinese or struggle with rare or outdated terms. MandarinTamer is designed to be a versatile tool for anyone in the Chinese linguistics field—whether you're a professor, translator, teacher, developer, or researcher—offering precision and flexibility for various applications, from localization to language education.

## Get Started

Install MandarinTamer from PyPI:

```bash
pip install mandarin-tamer
```

Basic usage:

```python
from mandarin_tamer import convert_mandarin_script

# Convert to Traditional (Taiwan)
trad = convert_mandarin_script("简体字", target_script="zh_tw")
print(trad)  # 簡體字

# Convert to Simplified
simp = convert_mandarin_script("繁體字", target_script="zh_cn")
print(simp)  # 繁体字

# Advanced options
text = convert_mandarin_script(
    "现代化的字",
    target_script="zh_tw",
    modernize=True,     # Replace archaic terms with modern ones
    normalize=True,     # Normalize character variants
    taiwanize=True,    # Use Taiwan-specific variants
    improved_one_to_many=True, # Use improved one-to-many mapping
    ner_list=["人名"], # List of NERs to include
    include_dicts={"name": ["name_dict.json"]}, # Include specific dictionaries
    exclude_lists={"name": ["name_exclude.json"]}, # Exclude specific dictionaries
)
```

For more examples and detailed documentation, visit our [GitHub repository](https://github.com/creolio/mandarinTamer) or [PyPi page](https://pypi.org/project/mandarin-tamer/).

### Original Developers

- **Jon Knebel** (Virginia, USA) – Full stack engineer + language educator + independent researcher of linguistics and language learning psychology.
- **Valeriu Celmare** (Romania) – Full stack engineer with a focus on Django and Python.

## Contributors

The dictionaries powering MandarinTamer have been made highly accurate for the top 10,000 Mandarin words, thanks to the contributions of professional translators from Taiwan, Hong Kong, and Mainland China. Special thanks to the following individuals for their valuable work in curating and verifying the dictionaries that power the tool:

Taiwan:

- **Rita J. Lee (李佩蓉)** – PhD in Chinese Literature; Taipei.
- **Jamie Chang (張汝禎)** - Taipei
- **Hsin Fang Wu** - Taipei
- **潘依依 (Elsie)** – Expert in modern and classical Mandarin; Taipei; <https://pse.is/754xk3>

Mainland China:

- **Zhou Yu**

Hong Kong:

- **Julia Yuen Ka Suen (袁嘉旋)**
- **Lok Yee Chan**

Their dedication and expertise have been crucial in ensuring the accuracy and reliability of MandarinTamer.
