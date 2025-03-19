# scripts/csv_conversion.py
import time
from pathlib import Path

import numpy as np
import pandas as pd

from mandarin_tamer.mandarin_tamer import convert_mandarin_script


def convert_csv_sentences(input_file: str, output_dir: str, target_script: str = "zh_cn") -> None:
    """Convert sentences in a CSV file from one script to another and back, with time tracking."""
    start_time = time.time()

    # Track process times
    process_times: dict[str, float] = {"read_csv": 0.0, "conversion": 0.0, "comparison": 0.0, "file_output": 0.0}

    # Read the input CSV file
    read_start = time.time()
    df = pd.read_csv(input_file)
    row_count = len(df)
    process_times["read_csv"] = time.time() - read_start

    # Get the opposite script for reconversion
    opposite_script = "zh_tw" if target_script == "zh_cn" else "zh_cn"

    # Process sentences in bulk instead of apply
    conversion_start = time.time()

    # Extract sentences to list for faster processing
    sentences = df.iloc[:, 0].tolist()

    # Convert all sentences at once
    converted_sentences: list[str] = []
    reconverted_sentences: list[str] = []

    # Measure just the conversion time
    pure_conversion_start = time.time()

    # Process each sentence but avoid pandas overhead
    for sentence in sentences:
        converted = convert_mandarin_script(sentence, target_script=target_script)
        converted_sentences.append(converted)
        reconverted = convert_mandarin_script(converted, target_script=opposite_script)
        reconverted_sentences.append(reconverted)

    process_times["conversion"] = time.time() - pure_conversion_start

    # Add results back to dataframe
    df["converted_sentence"] = converted_sentences
    df["reconverted_sentence"] = reconverted_sentences

    total_conversion_time = time.time() - conversion_start

    # Check if the reconverted sentence is the same as the original sentence
    comparison_start = time.time()
    df["same_as_original"] = np.array(reconverted_sentences) == df.iloc[:, 0].values
    process_times["comparison"] = time.time() - comparison_start

    # Create output filename
    input_path = Path(input_file)
    output_file = Path(output_dir) / f"tested_{input_path.name}"

    # Save to new CSV file
    output_start = time.time()
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    process_times["file_output"] = time.time() - output_start

    # Calculate time metrics
    total_time = time.time() - start_time
    avg_time_per_sentence = process_times["conversion"] / row_count if row_count else 0
    accounted_time = sum(process_times.values())
    unaccounted_time = total_time - accounted_time
    overhead_time = total_conversion_time - process_times["conversion"]

    # Print results with time metrics
    print(f"Conversion complete. Output saved to: {output_file}")
    print(f"Processed {row_count} rows in {total_time:.2f} seconds")
    print(f"Average conversion time per row: {avg_time_per_sentence * 1000:.2f} ms")
    print("\nProcess time breakdown:")
    print(
        f"  - CSV reading:         {process_times['read_csv']:.2f} seconds ({(process_times['read_csv'] / total_time) * 100:.1f}%)"
    )
    print(
        f"  - Character conversion: {process_times['conversion']:.2f} seconds ({(process_times['conversion'] / total_time) * 100:.1f}%)"
    )
    print(f"  - Processing overhead:  {overhead_time:.2f} seconds ({(overhead_time / total_time) * 100:.1f}%)")
    print(
        f"  - Result comparison:    {process_times['comparison']:.2f} seconds ({(process_times['comparison'] / total_time) * 100:.1f}%)"
    )
    print(
        f"  - File output:          {process_times['file_output']:.2f} seconds ({(process_times['file_output'] / total_time) * 100:.1f}%)"
    )
    print(f"  - Other operations:     {unaccounted_time:.2f} seconds ({(unaccounted_time / total_time) * 100:.1f}%)")
    print(f"  - Total time:           {total_time:.2f} seconds (100%)")


if __name__ == "__main__":
    input_csv = "sentence_csvs/trad_tatoeba_sentences_sample.csv"
    convert_csv_sentences(input_csv, output_dir="output", target_script="zh_cn")
