#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from const import MIN_LINE_CHARS, PAGE_SPLITTER, SPECIAL_CHARS


def remove_lines(text: str, min_chars: int = 10) -> str:
    """
    Removes lines from the input text that have less than `min_chars` characters.

    Args:
      text (str): The input text.
      min_chars (int, optional): The minimum number of characters required for a line to be considered valid. Defaults to 10.

    Returns:
      str: The input text with invalid lines removed.
    """

    # detect if the line has more than min_chars characters
    def is_valid_line(line):
        return len(line) >= min_chars

    lines = text.split("\n")
    lines = [line for line in lines if is_valid_line(line)]
    return "\n".join(lines)


def remove_duplicate_lines(text: str) -> str:
    """
    Removes duplicate lines from the input text.

    Args:
      text (str): The input text.

    Returns:
      str: The text with duplicate lines removed.
    """
    lines = text.split("\n")
    unique_lines = set()
    filtered_lines = []
    for line in lines:
        if line not in unique_lines:
            unique_lines.add(line)
            filtered_lines.append(line)
    return "\n".join(filtered_lines)


def clean_data(text: str) -> str:
    """
    This function takes in a string and removes any unwanted characters and lines from it.

    Args:
    - text (str): The input string to be cleaned.
    - min_chars (int): The minimum number of characters a line must have to be kept. Default is 3.

    Returns:
    - str: The cleaned string.
    """

    r = text.replace(PAGE_SPLITTER, "\n")
    r = r.translate(str.maketrans("", "", SPECIAL_CHARS))
    r = remove_lines(r, MIN_LINE_CHARS)
    return r
