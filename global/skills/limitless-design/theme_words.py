#!/usr/bin/env python3
"""Print a seed and five theme words picked from it. Omit the seed for a fresh roll."""

import argparse
import random
import secrets
from pathlib import Path

WORDS_FILE = Path(__file__).with_name("words.txt")
COUNT = 5


def load_words() -> list[str]:
    lines = WORDS_FILE.read_text(encoding="utf-8").splitlines()
    return sorted({line.strip() for line in lines if line.strip()})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seed", nargs="?", help="Reproduce an earlier roll; the same seed always gives the same words")
    args = parser.parse_args()
    seed = args.seed if args.seed is not None else secrets.token_hex(4)
    print(f"seed: {seed}")
    for word in random.Random(seed).sample(load_words(), COUNT):
        print(word)


if __name__ == "__main__":
    main()
