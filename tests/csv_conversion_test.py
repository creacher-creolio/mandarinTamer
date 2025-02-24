import sys
import time
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))

from src.mandarin_tamer import convert_mandarin_script


def convert_csv_sentences(input_file: str | Path, output_dir: str | Path, target_script: str = "zh_cn") -> None:
    start_time = time.time()

    # Convert input_file to Path if it's a string
    input_path = Path(input_file)
    # If the path doesn't exist, try to resolve it relative to the script directory
    if not input_path.exists():
        input_path = Path(__file__).parent / input_file

    # Read the input CSV file
    df = pd.read_csv(input_path)

    # Get the opposite script for reconversion
    opposite_script = "zh_tw" if target_script == "zh_cn" else "zh_cn"

    # Convert sentences to target script and then back
    df["converted_sentence"] = df.iloc[:, 0].apply(lambda x: convert_mandarin_script(x, target_script=target_script))
    df["reconverted_sentence"] = df["converted_sentence"].apply(
        lambda x: convert_mandarin_script(x, target_script=opposite_script)
    )

    # Check if the reconverted sentence is the same as the original sentence
    df["same_as_original"] = df["reconverted_sentence"] == df.iloc[:, 0]

    # Create output directory path relative to script location
    output_path = Path(__file__).parent / output_dir
    output_file = output_path / f"tested_{input_path.name}"

    # Save to new CSV file
    output_path.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Conversion complete. Output saved to: {output_file}")
    print(f"Total conversion time: {time.time() - start_time:.3f}s")


input_csv = "sentence_csvs/trad_tatoeba_sentences_sample.csv"
convert_csv_sentences(input_csv, output_dir="output", target_script="zh_cn")
