# scripts/csv_conversion.py
import contextlib
import io
import sys
import time
from pathlib import Path

import pandas as pd

# Add the src directory to path so we can import the mandarin_tamer module
sys.path.append(str(Path(__file__).parent.parent))

# Import individual functions to time them
from src.mandarin_tamer.mandarin_tamer_2 import (
    detaiwanize_characters,
    detaiwanize_phrases,
    modernize_simplified,
    modernize_traditional,
    normalize_simplified,
    normalize_traditional,
    simplify_characters,
    simplify_one_to_many,
    simplify_phrases,
    taiwanize_characters,
    taiwanize_phrases,
    traditionalize_characters,
    traditionalize_one_to_many,
    traditionalize_phrases,
)


def timed_function(func):
    """Decorator to time function execution"""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        wrapper.total_time += execution_time
        wrapper.call_count += 1
        return result

    wrapper.total_time = 0.0
    wrapper.call_count = 0
    wrapper.__name__ = func.__name__
    return wrapper


def convert_csv_sentences(input_file: str, output_dir: str, target_script: str = "zh_cn") -> None:
    """Convert sentences in a CSV file from one script to another and back, with time tracking."""
    start_time = time.time()

    # Track process times
    process_times: dict[str, float] = {"read_csv": 0.0, "conversion": 0.0, "comparison": 0.0, "file_output": 0.0}

    # Create timed versions of all functions
    timed_functions = {
        "modernize_simplified": timed_function(modernize_simplified),
        "normalize_simplified": timed_function(normalize_simplified),
        "traditionalize_phrases": timed_function(traditionalize_phrases),
        "traditionalize_one_to_many": timed_function(traditionalize_one_to_many),
        "traditionalize_characters": timed_function(traditionalize_characters),
        "modernize_traditional": timed_function(modernize_traditional),
        "normalize_traditional": timed_function(normalize_traditional),
        "taiwanize_phrases": timed_function(taiwanize_phrases),
        "taiwanize_characters": timed_function(taiwanize_characters),
        "detaiwanize_phrases": timed_function(detaiwanize_phrases),
        "detaiwanize_characters": timed_function(detaiwanize_characters),
        "simplify_phrases": timed_function(simplify_phrases),
        "simplify_one_to_many": timed_function(simplify_one_to_many),
        "simplify_characters": timed_function(simplify_characters),
    }

    # Define custom transliteration functions using timed functions
    def timed_custom_to_tw_trad(sentence: str) -> str:
        steps = [
            timed_functions["modernize_simplified"],
            timed_functions["normalize_simplified"],
            timed_functions["traditionalize_phrases"],
            timed_functions["traditionalize_one_to_many"],
            timed_functions["traditionalize_characters"],
            timed_functions["modernize_traditional"],
            timed_functions["normalize_traditional"],
            timed_functions["taiwanize_phrases"],
            timed_functions["taiwanize_characters"],
        ]
        for step in steps:
            sentence = step(sentence)
        return sentence

    def timed_custom_to_simp(sentence: str) -> str:
        steps = [
            timed_functions["modernize_traditional"],
            timed_functions["normalize_traditional"],
            timed_functions["detaiwanize_phrases"],
            timed_functions["detaiwanize_characters"],
            timed_functions["simplify_phrases"],
            timed_functions["simplify_one_to_many"],
            timed_functions["simplify_characters"],
            timed_functions["modernize_simplified"],
            timed_functions["normalize_simplified"],
        ]
        for step in steps:
            sentence = step(sentence)
        return sentence

    def timed_custom_transliteration(orig_sentence: str, target_script: str = "") -> str:
        return (
            timed_custom_to_tw_trad(orig_sentence)
            if target_script == "to_tw_trad"
            else timed_custom_to_simp(orig_sentence)
        )

    # Read the input CSV file
    read_start = time.time()
    df = pd.read_csv(input_file)
    row_count = len(df)
    process_times["read_csv"] = time.time() - read_start

    # Map target script to mandarin_tamer function parameter
    target_param = "to_tw_trad" if target_script == "to_tw_trad" else ""
    # Get the opposite script for reconversion
    # opposite_script = "" if target_script == "to_tw_trad" else "to_tw_trad"
    # opposite_param = "" if opposite_script == "to_tw_trad" else "to_tw_trad"

    # Process sentences in bulk instead of apply
    conversion_start = time.time()

    # Extract sentences to list for faster processing
    sentences = df.iloc[:, 0].tolist()

    # Convert all sentences at once
    converted_sentences: list[str] = []
    # reconverted_sentences: list[str] = []

    # Measure just the conversion time
    pure_conversion_start = time.time()

    # Suppress print output from custom_transliteration
    null_output = io.StringIO()

    # Process each sentence but avoid pandas overhead
    for sentence in sentences:
        # Suppress debug prints from conversion functions
        with contextlib.redirect_stdout(null_output):
            converted = timed_custom_transliteration(sentence, target_script=target_param)
            converted_sentences.append(converted)
            # reconverted = timed_custom_transliteration(converted, target_script=opposite_param)
            # reconverted_sentences.append(reconverted)

    process_times["conversion"] = time.time() - pure_conversion_start

    # Add results back to dataframe
    df["converted_sentence"] = converted_sentences
    # df["reconverted_sentence"] = reconverted_sentences

    total_conversion_time = time.time() - conversion_start

    # Check if the reconverted sentence is the same as the original sentence
    comparison_start = time.time()
    # df["same_as_original"] = np.array(reconverted_sentences) == df.iloc[:, 0].values
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

    # Print detailed function timing
    print("\nDetailed function timing:")

    # Sort functions by total time (descending)
    sorted_functions = sorted(timed_functions.items(), key=lambda x: x[1].total_time, reverse=True)

    for func_name, func in sorted_functions:
        if func.call_count > 0:
            avg_time = (func.total_time / func.call_count) * 1000  # ms
            pct_of_total = (func.total_time / process_times["conversion"]) * 100
            print(
                f"  - {func_name}: {func.total_time:.2f}s total, {avg_time:.2f}ms avg ({pct_of_total:.1f}% of conversion)"
            )


if __name__ == "__main__":
    # input_csv = "tests/sentence_csvs/trad_tatoeba_sentences_sample.csv"
    # convert_csv_sentences(input_csv, output_dir="tests/output", target_script="zh_cn")
    input_csv = "tests/sentence_csvs/simp_tatoeba_sentences_sample.csv"
    convert_csv_sentences(input_csv, output_dir="tests/output", target_script="to_tw_trad")
