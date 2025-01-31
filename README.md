# MandarinTamer  

MandarinTamer is a Python library for converting Mandarin text between Simplified Chinese and Traditional Chinese, with a focus on the Taiwanese variant. It’s designed to be accurate, flexible, and easy to use.  

## What Makes MandarinTamer Unique?  

MandarinTamer stands out for its ability to convert text without requiring prior knowledge of the input script. It seamlessly handles Simplified, all forms of Traditional, or even mixed-script text, automatically transforming it into your desired script.  

It also offers:  

- **Modernization and Normalization**: Replace rare or outdated terms with more commonly used equivalents.  
- **AI-Powered Context Awareness**: Uses sentence context with AI to intelligently resolve one-to-many mappings.  

## Key Features  

- **Simplified ↔ Taiwanese Traditional Conversion**: Handle text transformation with precision, adhering to regional linguistic norms.  
- **Context-Free Accuracy**: Achieves high accuracy without requiring metadata or prior knowledge of the input text.  
- **Modernization and Normalization**: Optionally modernize rare or archaic words into their more commonly used equivalents.  
- **Taiwanese-Centric Focus**: Optimized for Taiwanese writing conventions, perfect for localization and Taiwanese content.  
- **Open Source**: Built for developers and researchers to adapt, enhance, and integrate into other projects.  

## Why MandarinTamer?  

Traditional conversion tools often fail to capture the nuances of regional variants like Taiwanese Traditional Chinese or struggle with rare or outdated terms. MandarinTamer is designed to be a versatile tool for anyone in the Chinese linguistics field—whether you're a professor, translator, teacher, developer, or researcher—offering precision and flexibility for various applications, from localization to language education.

## Get Started  

To get started with MandarinTamer, simply install the package via pip:

```bash
pip install mandarinTamer
```

Once installed, you can use it to convert text to Simplified or Taiwanese Traditional Mandarin with a few lines of code. Here’s a quick example:

```python
from mandarinTamer import convert

mandarin_text = "简体字"
traditional_text = convert(mandarin_text, target_script="traditional_taiwan")
print(traditional_text)
```

### Original Developers

- **Jon Knebel** (Virginia, USA) – Full stack engineer + language educator + independent researcher of linguistics and language learning psychology.
- **Valeriu Celmare** (Romania) – Full stack engineer with a focus on Django and Python.

## Contributors  

The dictionaries powering MandarinTamer have been made highly accurate for the top 10,000 Mandarin words, thanks to the contributions of professional translators from Taiwan, Hong Kong, and Mainland China. Special thanks to the following individuals for their valuable work in curating and verifying the dictionaries that power the tool:

- **Translator 1** (Taipei, Taiwan) – Expertise in modern and classical Mandarin.
- **Translator 2** (Kaohsiung, Taiwan) – Specialist in traditional Chinese literature and linguistics.
- **Translator 3** (Tainan, Taiwan) – Focus on regional language variants and cultural nuances.

Their dedication and expertise have been crucial in ensuring the accuracy and reliability of MandarinTamer.
