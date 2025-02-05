import csv
import json
from pathlib import Path


def compare_json_dictionaries(
    csv_file: Path,
    json_file1: Path,
    json_file2: Path,
    json_file3: Path,
    output_only_in_file1: Path,
    output_only_in_file2: Path,
    output_only_in_file3: Path,
    output_common_in_all: Path,
    output_common_in_one_and_two: Path,
    output_common_in_one_and_three: Path,
    output_common_in_two_and_three: Path,
):
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        gls_terms_order = [row["gls_term"] for row in reader]

    with open(json_file1, encoding="utf-8") as f:
        json_dict1 = json.load(f)
    with open(json_file2, encoding="utf-8") as f:
        json_dict2 = json.load(f)
    with open(json_file3, encoding="utf-8") as f:
        json_dict3 = json.load(f)

    keys1 = set(json_dict1.keys())
    keys2 = set(json_dict2.keys())
    keys3 = set(json_dict3.keys())

    # Keys found in all three dictionaries
    common_in_all = keys1 & keys2 & keys3

    # Keys unique to each dictionary
    only_in_file1 = keys1 - (keys2 | keys3)
    only_in_file2 = keys2 - (keys1 | keys3)
    only_in_file3 = keys3 - (keys1 | keys2)

    # Keys shared by exactly two dictionaries
    common_in_two = (keys1 & keys2) | (keys1 & keys3) | (keys2 & keys3) - common_in_all

    # Sort the results by the order in the CSV file
    sorted_common_in_all = {
        key: json_dict1.get(key, json_dict2.get(key, json_dict3.get(key)))
        for key in gls_terms_order
        if key in common_in_all
    }
    sorted_only_in_file1 = {key: json_dict1[key] for key in gls_terms_order if key in only_in_file1}
    sorted_only_in_file2 = {key: json_dict2[key] for key in gls_terms_order if key in only_in_file2}
    sorted_only_in_file3 = {key: json_dict3[key] for key in gls_terms_order if key in only_in_file3}
    sorted_common_in_one_and_two = {
        key: json_dict1.get(key, json_dict2.get(key)) for key in gls_terms_order if key in common_in_two
    }
    sorted_common_in_one_and_three = {
        key: json_dict1.get(key, json_dict3.get(key)) for key in gls_terms_order if key in common_in_two
    }
    sorted_common_in_two_and_three = {
        key: json_dict2.get(key, json_dict3.get(key)) for key in gls_terms_order if key in common_in_two
    }

    # Write the results to the corresponding output files
    with open(output_only_in_file1, "w", encoding="utf-8") as f:
        json.dump(sorted_only_in_file1, f, ensure_ascii=False, indent=4)

    with open(output_only_in_file2, "w", encoding="utf-8") as f:
        json.dump(sorted_only_in_file2, f, ensure_ascii=False, indent=4)

    with open(output_only_in_file3, "w", encoding="utf-8") as f:
        json.dump(sorted_only_in_file3, f, ensure_ascii=False, indent=4)

    with open(output_common_in_all, "w", encoding="utf-8") as f:
        json.dump(sorted_common_in_all, f, ensure_ascii=False, indent=4)

    with open(output_common_in_one_and_two, "w", encoding="utf-8") as f:
        json.dump(sorted_common_in_one_and_two, f, ensure_ascii=False, indent=4)

    with open(output_common_in_one_and_three, "w", encoding="utf-8") as f:
        json.dump(sorted_common_in_one_and_three, f, ensure_ascii=False, indent=4)

    with open(output_common_in_two_and_three, "w", encoding="utf-8") as f:
        json.dump(sorted_common_in_two_and_three, f, ensure_ascii=False, indent=4)


def main():
    current_dir = Path(__file__).resolve().parent

    compare_json_dictionaries(
        current_dir / "../../cedict_top_64k.csv",
        current_dir / "s2t_amb_cedict.json",
        current_dir / "s2t_amb_opencc.json",
        current_dir / "s2t_amb_wikipedia.json",
        current_dir / "output/s2t_amb_cedict_only.json",
        current_dir / "output/s2t_amb_opencc_only.json",
        current_dir / "output/s2t_amb_wikipedia_only.json",
        current_dir / "output/s2t_amb_common_all.json",
        current_dir / "output/s2t_amb_cedict_opencc.json",
        current_dir / "output/s2t_amb_cedict_wikipedia.json",
        current_dir / "output/s2t_amb_opencc_wikipedia.json",
    )


if __name__ == "__main__":
    main()
