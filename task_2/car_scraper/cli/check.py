# You can use this script to save cars.
import argparse
import os

from ..great_ex import process_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="Path to car file", type=str)
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        exit("file_path doesn't exist")

    process_file(args.file_path)


if __name__ == "__main__":
    main()
