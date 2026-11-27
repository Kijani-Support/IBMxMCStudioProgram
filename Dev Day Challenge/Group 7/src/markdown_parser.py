"""Small Markdown table and heading helpers with source line positions."""
import re


def cells(line: str) -> list[str]:
    return [part.strip().strip("*") for part in line.strip().strip("|").split("|")]


def is_separator(line: str) -> bool:
    return bool(re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", line))


def tables(lines: list[str], start: int, end: int) -> list[tuple[int, list[list[str]]]]:
    found = []
    i = start
    while i < end:
        if "|" not in lines[i]:
            i += 1
            continue
        j = i
        block = []
        while j < end and "|" in lines[j]:
            if not is_separator(lines[j]):
                block.append((j + 1, cells(lines[j])))
            j += 1
        if len(block) >= 2:
            found.append((block[0][0], [row for _, row in block[1:]]))
        i = j
    return found
