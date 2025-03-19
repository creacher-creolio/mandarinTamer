# scripts/csv_conversion.py
import time
from pathlib import Path

import pandas as pd

from mandarin_tamer.mandarin_tamer import convert_mandarin_script


def convert_csv_sentences(input_file: str, output_dir: str, target_script: str = "zh_cn") -> None:
    """Convert sentences in a CSV file from one script to another and back, with time tracking."""
    start_time = time.time()

    # Track process times
    process_times = {"read_csv": 0, "conversion": 0, "conversion_overhead": 0, "comparison": 0, "file_output": 0}

    # Read the input CSV file
    read_start = time.time()
    df = pd.read_csv(input_file)
    row_count = len(df)
    process_times["read_csv"] = time.time() - read_start

    # Get the opposite script for reconversion
    opposite_script = "zh_tw" if target_script == "zh_cn" else "zh_cn"

    # Track conversion times for each row
    row_times = []

    # Function to time individual row conversion
    def timed_convert(text, target):
        row_start = time.time()
        result = convert_mandarin_script(text, target_script=target)
        row_times.append(time.time() - row_start)
        return result

    # Convert sentences to target script and then back
    conversion_start = time.time()
    df["converted_sentence"] = df.iloc[:, 0].apply(lambda x: timed_convert(x, target_script))
    df["reconverted_sentence"] = df["converted_sentence"].apply(
        lambda x: convert_mandarin_script(x, target_script=opposite_script)
    )
    total_conversion_time = time.time() - conversion_start

    # Calculate actual conversion time vs pandas/apply overhead
    conversion_only_time = sum(row_times)
    process_times["conversion"] = conversion_only_time
    process_times["conversion_overhead"] = total_conversion_time - conversion_only_time

    # Check if the reconverted sentence is the same as the original sentence
    comparison_start = time.time()
    df["same_as_original"] = df["reconverted_sentence"] == df.iloc[:, 0]
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
    avg_time_per_row = sum(row_times) / len(row_times) if row_times else 0
    accounted_time = sum(process_times.values())
    unaccounted_time = total_time - accounted_time

    # Print results with time metrics
    print(f"Conversion complete. Output saved to: {output_file}")
    print(f"Processed {row_count} rows in {total_time:.2f} seconds")
    print(f"Average conversion time per row: {avg_time_per_row * 1000:.2f} ms")
    print("\nProcess time breakdown:")
    print(
        f"  - CSV reading:        {process_times['read_csv']:.2f} seconds ({(process_times['read_csv'] / total_time) * 100:.1f}%)"
    )
    print(
        f"  - Character conversion: {process_times['conversion']:.2f} seconds ({(process_times['conversion'] / total_time) * 100:.1f}%)"
    )
    print(
        f"  - Pandas/apply overhead: {process_times['conversion_overhead']:.2f} seconds ({(process_times['conversion_overhead'] / total_time) * 100:.1f}%)"
    )
    print(
        f"  - Result comparison:  {process_times['comparison']:.2f} seconds ({(process_times['comparison'] / total_time) * 100:.1f}%)"
    )
    print(
        f"  - File output:        {process_times['file_output']:.2f} seconds ({(process_times['file_output'] / total_time) * 100:.1f}%)"
    )
    print(f"  - Other operations:   {unaccounted_time:.2f} seconds ({(unaccounted_time / total_time) * 100:.1f}%)")
    print(f"  - Total time:         {total_time:.2f} seconds (100%)")


if __name__ == "__main__":
    input_csv = "sentence_csvs/trad_tatoeba_sentences_sample.csv"
    convert_csv_sentences(input_csv, output_dir="output", target_script="zh_cn")
