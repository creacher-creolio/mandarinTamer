# tests/conversion_test_2.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

# Test for MandarinConverter main conversion function
from src.mandarin_tamer.mandarin_tamer_2 import MandarinConverter


def test_convert_script():
    converter = MandarinConverter(debug=True)
    sentence = "中国的颜色很漂亮。"
    # Test to_tw_trad (Taiwan traditional)
    result = converter.convert_script(sentence, target_script="to_tw_trad", debug=True)

    # When debug is True, result is a dictionary with 'result' and 'timings'
    print(f"Converted text: {result['result']}")
    print("\nTiming information:")
    for step, timing_data in result["timings"].items():
        if step == "total_major":
            print(f"Total conversion time: {timing_data:.5f} seconds")
        elif isinstance(timing_data, dict):
            print(f"\n{step}:")
            for timing_type, timing_value in timing_data.items():
                if timing_type == "major":
                    print(f"  Step time: {timing_value:.5f} seconds")
                elif isinstance(timing_value, float):
                    print(f"  {timing_type}: {timing_value:.5f} seconds")


if __name__ == "__main__":
    test_convert_script()
