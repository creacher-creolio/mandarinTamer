# scripts/csv_conversion.py
import sys
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd

# Add the src directory to path so we can import the mandarin_tamer module
sys.path.append(str(Path(__file__).parent.parent))

# Import individual functions to time them
from src.mandarin_tamer.mandarin_tamer_2 import MandarinConverter


def convert_csv_sentences(input_file: str, output_dir: str, target_script: str = "zh_cn") -> None:
    # Read the input CSV file
    df = pd.read_csv(input_file)

    # Initialize converter
    converter = MandarinConverter(debug=True)

    # Prepare result containers
    results = []
    total_time: float = 0.0
    major_steps_total: dict[str, float] = defaultdict(float)
    minor_steps_timing: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    micro_steps_total: dict[str, float] = defaultdict(float)

    # Process each sentence
    for idx, row in df.iterrows():
        sentence = row["original_sentence"]
        start_time = time.time()

        # Get conversion result with timing information
        conversion_result = converter.convert_script(sentence, target_script=target_script, debug=True)

        # Calculate time for this conversion
        sentence_time = time.time() - start_time
        total_time += sentence_time

        # Extract timing information
        timings = conversion_result["timings"]

        # Accumulate step timings
        for step_name, step_details in timings.items():
            # In the updated structure, step_details contains only the minor step timings
            # Calculate and store the major step total (sum of all its minor steps)
            step_total = sum(step_details.values())
            major_steps_total[step_name] += step_total

            # Accumulate minor step timings
            for sub_step, sub_time in step_details.items():
                minor_steps_timing[step_name][sub_step] += sub_time
                micro_steps_total[sub_step] += sub_time  # Track totals for each micro step

        # Append results
        results.append({"original": sentence, "converted": conversion_result["result"]})

    # Print timing information
    print(f"{total_time:.2f} sec - TOTAL TIME\n")

    # Print major and minor step timings
    for major_step, major_total in major_steps_total.items():
        print(f"{major_total:.2f} sec - {major_step}")

        # Print minor steps for this major step
        if major_step in minor_steps_timing:
            for sub_step, sub_time in minor_steps_timing[major_step].items():
                print(f"     {sub_time:.2f} sec - {sub_step}")
        print()

    # Add a horizontal rule
    print("-" * 50)
    print("\n")

    # Print micro step totals across all conversions
    for micro_step, micro_time in micro_steps_total.items():
        print(f"{micro_time:.2f} sec - TOTAL {micro_step}")

    # Repeat total time
    print(f"\n{total_time:.2f} sec - TOTAL TIME\n")

    # Save results to output file if needed
    output_path = Path(output_dir) / f"{Path(input_file).stem}_{target_script}_output.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_path, index=False)
    print(f"Converted results saved to {output_path}")


if __name__ == "__main__":
    # input_csv = "tests/sentence_csvs/trad_tatoeba_sentences_sample.csv"
    # convert_csv_sentences(input_csv, output_dir="tests/output", target_script="zh_cn")
    input_csv = "tests/sentence_csvs/simp_tatoeba_sentences_sample.csv"
    convert_csv_sentences(input_csv, output_dir="tests/output", target_script="to_tw_trad")
