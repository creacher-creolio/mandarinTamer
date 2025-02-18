import json
from pathlib import Path


class FileConversion:
    @staticmethod
    def json_to_dict(file_path) -> dict:
        with Path(file_path).open() as file:
            return json.load(file)

    @staticmethod
    def tsv_1_to_1_to_dict(file_path) -> dict:
        return FileConversion.tsv_to_dict(file_path, lambda x: x)

    @staticmethod
    def tsv_1_to_many_to_dict(file_path) -> dict:
        return FileConversion.tsv_to_dict(file_path, lambda x: x.split())

    @staticmethod
    def tsv_1_to_first_many_to_dict(file_path) -> dict:
        return FileConversion.tsv_to_dict(file_path, lambda x: x.split()[0])

    @staticmethod
    def tsv_to_dict(file_path, split_func) -> dict:
        with Path(file_path).open() as file:
            return {
                line.split("\t")[0]: split_func(line.split("\t")[1].strip())
                for line in file
                if "\t" in line and len(line.split("\t")) > 1
            }
