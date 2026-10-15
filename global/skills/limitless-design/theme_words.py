#!/usr/bin/env python3
"""Print five theme words picked deterministically from a seed string."""

import argparse
import random
from pathlib import Path

WORDS_FILE = Path(__file__).with_name("words.txt")
COUNT = 5


def load_words() -> list[str]:
    lines = WORDS_FILE.read_text(encoding="utf-8").splitlines()
    return sorted({line.strip() for line in lines if line.strip()})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seed", help="Any string; the same seed always gives the same words")
    args = parser.parse_args()
    for word in random.Random(args.seed).sample(load_words(), COUNT):
        print(word)


if __name__ == "__main__":
    main()
