# scripts/csv_conversion.py
import time
from pathlib import Path

import numpy as np
import pandas as pd

from mandarin_tamer.helpers.conversion_config import SCRIPT_RESET_STEPS, get_conversion_steps
from mandarin_tamer.helpers.conversion_operations import ConversionOperation
from mandarin_tamer.mandarin_tamer import ScriptConverter


class TimedScriptConverter(ScriptConverter):
    """Extended converter class that tracks time for each conversion step."""

    def __init__(self, *args, **kwargs):
        self.step_times = {
            "initialization": 0.0,
            "dict_loading": 0.0,
            "phrase_conversion": 0.0,
            "one2many_conversion": 0.0,
            "char_conversion": 0.0,
        }
        self.config_times = {}

        # Track initialization time
        start = time.time()
        super().__init__(*args, **kwargs)
        self.step_times["initialization"] = time.time() - start

    def load_config(self, config):
        """Override to track dictionary loading time."""
        start = time.time()
        result = super().load_config(config)
        self.step_times["dict_loading"] += time.time() - start
        return result

    def apply_conversion(self, sentence, config, current_indexes=None):
        """Override to track individual conversion steps."""
        if config.name not in self.config_times:
            self.config_times[config.name] = 0.0

        config_start = time.time()

        # Load configuration dictionaries if needed
        if config.name not in self.dicts:
            start = time.time()
            self.load_config(config)
            self.step_times["dict_loading"] += time.time() - start

        dicts = self.dicts[config.name]
        new_sentence = sentence

        # Always include NER indexes in current_indexes
        current_indexes = list(set(current_indexes or []) | set(self.ner_indexes))

        # Determine if we should reset indexes for script conversion steps
        should_reset_indexes = config.name in SCRIPT_RESET_STEPS and dicts["phrase"] and any(dicts["phrase"].values())
        phrase_indexes = self.ner_indexes if should_reset_indexes else current_indexes

        # Apply phrase conversion if dictionary is not empty
        if dicts["phrase"] and any(dicts["phrase"].values()):
            start = time.time()
            operation = ConversionOperation(new_sentence, phrase_indexes)
            new_sentence, phrase_indexes = operation.apply_phrase_conversion(dicts["phrase"])
            self.step_times["phrase_conversion"] += time.time() - start

        # Apply one-to-many conversion if available
        if dicts["one2many"] and (config.openai_func or config.opencc_config):
            start = time.time()
            operation = ConversionOperation(new_sentence, phrase_indexes)

            # Fix the call by only passing the arguments that the method accepts
            if self.improved_one_to_many and config.openai_func:
                # When using improved mode, we need the OpenAI function and client
                new_sentence = operation.apply_one_to_many_conversion(
                    mapping_dict=dicts["one2many"],
                    use_improved_mode=self.improved_one_to_many,
                    openai_func=config.openai_func,
                    openai_client=self.openai_client,
                )
            else:
                # When using OpenCC mode, we only need the OpenCC config
                new_sentence = operation.apply_one_to_many_conversion(
                    mapping_dict=dicts["one2many"],
                    use_improved_mode=self.improved_one_to_many,
                    opencc_config=config.opencc_config,
                )

            self.step_times["one2many_conversion"] += time.time() - start

        # Apply character conversion
        start = time.time()
        operation = ConversionOperation(new_sentence, phrase_indexes)
        result = operation.apply_char_conversion(dicts["char"])
        self.step_times["char_conversion"] += time.time() - start

        # Track time per config
        self.config_times[config.name] += time.time() - config_start

        return result


def timed_convert_mandarin_script(sentence, target_script="zh_cn", **kwargs):
    """Timed version of convert_mandarin_script that returns timing details."""
    converter = TimedScriptConverter(sentence=sentence, target_script=target_script, **kwargs)

    # Time the overall conversion
    start = time.time()
    result = converter.convert()
    total_time = time.time() - start

    return result, total_time, converter.step_times, converter.config_times


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

    # Track detailed conversion step times
    detailed_step_times = {
        "initialization": 0.0,
        "dict_loading": 0.0,
        "phrase_conversion": 0.0,
        "one2many_conversion": 0.0,
        "char_conversion": 0.0,
    }

    # Track time by configuration type
    config_times = {}

    # Get the conversion sequence for reporting
    flags = {"modernize": True, "normalize": True, "taiwanize": True}
    target_conversion_steps = get_conversion_steps(target_script, flags)
    opposite_conversion_steps = get_conversion_steps(opposite_script, flags)

    for step in target_conversion_steps + opposite_conversion_steps:
        config_times[step] = 0.0

    # Measure just the conversion time
    pure_conversion_start = time.time()

    # Process each sentence but avoid pandas overhead
    for sentence in sentences:
        # Forward conversion with timing
        converted, _, step_times, cfg_times = timed_convert_mandarin_script(sentence, target_script=target_script)
        converted_sentences.append(converted)

        # Backward conversion with timing
        reconverted, _, reverse_step_times, reverse_cfg_times = timed_convert_mandarin_script(
            converted, target_script=opposite_script
        )
        reconverted_sentences.append(reconverted)

        # Accumulate time stats
        for k, v in step_times.items():
            detailed_step_times[k] += v
        for k, v in reverse_step_times.items():
            detailed_step_times[k] += v

        # Accumulate config times
        for k, v in cfg_times.items():
            if k in config_times:
                config_times[k] += v
        for k, v in reverse_cfg_times.items():
            if k in config_times:
                config_times[k] += v

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

    # Calculate percentages for step times
    step_percentages = {k: (v / process_times["conversion"]) * 100 for k, v in detailed_step_times.items()}

    # Calculate percentages for config times
    cfg_percentages = {k: (v / process_times["conversion"]) * 100 for k, v in config_times.items()}

    # Sort configs by time for reporting
    sorted_configs = sorted(config_times.items(), key=lambda x: x[1], reverse=True)

    # Calculate overhead and unaccounted time
    overhead_time = total_conversion_time - process_times["conversion"]
    accounted_time = sum(process_times.values())
    unaccounted_time = total_time - accounted_time

    # Print results with time metrics
    print(f"Conversion complete. Output saved to: {output_file}")
    print(f"Processed {row_count} rows in {total_time:.2f} seconds")

    # Print detailed breakdown of conversion substeps
    print("\nConversion substeps breakdown:")
    for step, time_value in sorted(detailed_step_times.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {step:<20} {time_value:.2f} seconds ({step_percentages[step]:.1f}%)")

    # Print conversion configs breakdown
    print("\nConversion configuration breakdown:")
    for config, time_value in sorted_configs:
        if time_value > 0:
            print(f"  - {config:<20} {time_value:.2f} seconds ({cfg_percentages[config]:.1f}%)")

    # Print overall process breakdown
    print("\nOverall process breakdown:")
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
    input_csv = "tests/sentence_csvs/trad_tatoeba_sentences_sample.csv"
    convert_csv_sentences(input_csv, output_dir="tests/output", target_script="zh_cn")
