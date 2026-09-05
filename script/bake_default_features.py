#!/usr/bin/env python3
"""Copy selected alternate glyph layers onto their default glyphs."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


FEATURE_MAPPINGS = {
    "cv02": [
        ("g", "g.cv02"),
        ("gbreve", "gbreve.cv02"),
        ("gcircumflex", "gcircumflex.cv02"),
        ("gcommaaccent", "gcommaaccent.cv02"),
        ("gdotaccent", "gdotaccent.cv02"),
    ],
    "cv10": [
        ("l", "l.cv10"),
        ("lacute", "lacute.cv10"),
        ("lcaron", "lcaron.cv10"),
        ("lcommaaccent", "lcommaaccent.cv10"),
        ("ldot", "ldot.cv10"),
        ("lslash", "lslash.cv10"),
    ],
    "cv16": [
        # The root asterisk glyphs are exchanged simultaneously. Their .lc
        # and .cv15 forms use components and inherit the exchange.
        ("asterisk", "asteriskmath"),
        ("asteriskmath", "asterisk"),
        ("asterisk_asterisk.liga", "asterisk_asterisk.liga.cv16"),
        ("asterisk_asterisk_asterisk.liga", "asterisk_asterisk_asterisk.liga.cv16"),
        ("asterisk_slash.liga", "asterisk_slash.liga.cv16"),
        ("slash_asterisk.liga", "slash_asterisk.liga.cv16"),
        ("less_asterisk.liga", "less_asterisk.liga.cv16"),
        ("less_asterisk_greater.liga", "less_asterisk_greater.liga.cv16"),
        ("asterisk_greater.liga", "asterisk_greater.liga.cv16"),
    ],
    "cv29": [
        ("braceleft", "braceleft.cv29"),
        ("braceright", "braceright.cv29"),
        ("numbersign_braceleft.liga", "numbersign_braceleft.liga.cv29"),
    ],
    "ss01": [("r", "r.ss01")],
    "ss03": [
        ("ampersand", "ampersand.ss03"),
        ("ampersand_ampersand.liga", "ampersand_ampersand.liga.ss03"),
    ],
    "ss05": [("at", "at.ss05")],
    "zero": [
        ("zero", "zero.zero"),
        ("zero.tosf", "zero.tosf.zero"),
    ],
}


def matching_delimiter(text: str, start: int, opening: str, closing: str) -> int:
    """Return the matching delimiter while ignoring delimiters in strings."""
    if text[start] != opening:
        raise ValueError(f"Expected {opening!r} at offset {start}")

    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index

    raise ValueError(f"Unmatched {opening!r} at offset {start}")


def glyph_object(text: str, glyph_name: str) -> tuple[int, int, str]:
    marker = f"glyphname = {glyph_name};"
    marker_start = text.find(marker)
    if marker_start < 0:
        raise ValueError(f"Missing glyph: {glyph_name}")
    if text.find(marker, marker_start + len(marker)) >= 0:
        raise ValueError(f"Duplicate glyph: {glyph_name}")

    object_start = text.rfind("\n{\n", 0, marker_start)
    if object_start < 0:
        raise ValueError(f"Cannot find object start for glyph: {glyph_name}")
    object_start += 1
    object_end = matching_delimiter(text, object_start, "{", "}") + 1
    return object_start, object_end, text[object_start:object_end]


def layers_assignment(glyph_text: str, glyph_name: str) -> str:
    marker = "layers = ("
    assignment_start = glyph_text.find(marker)
    if assignment_start < 0:
        raise ValueError(f"Missing layers for glyph: {glyph_name}")
    paren_start = assignment_start + len("layers = ")
    paren_end = matching_delimiter(glyph_text, paren_start, "(", ")")
    if glyph_text[paren_end + 1] != ";":
        raise ValueError(f"Malformed layers for glyph: {glyph_name}")
    return glyph_text[assignment_start : paren_end + 2]


def replace_layers(text: str, mappings: list[tuple[str, str]]) -> str:
    # Take every source snapshot before replacing anything. This is required
    # for cv16, which exchanges asterisk and asteriskmath.
    source_layers = {}
    for _, source_name in mappings:
        if source_name not in source_layers:
            _, _, source_object = glyph_object(text, source_name)
            source_layers[source_name] = layers_assignment(source_object, source_name)

    replacements = []
    for target_name, source_name in mappings:
        object_start, _, target_object = glyph_object(text, target_name)
        old_layers = layers_assignment(target_object, target_name)
        layers_start = object_start + target_object.find(old_layers)
        replacements.append(
            (layers_start, layers_start + len(old_layers), source_layers[source_name])
        )

    for start, end, replacement in sorted(replacements, reverse=True):
        text = text[:start] + replacement + text[end:]
    return text


def remove_tilde_at_lookup(text: str) -> str:
    # ss05 cancels Fira Code's special ~@ composition. With the selected @
    # drawing copied onto the cmap glyph, removing only this calt lookup makes
    # ~@ render as two ordinary default glyphs without any required feature.
    pattern = re.compile(r"\nlookup asciitilde_at \{.*?\n\} asciitilde_at;", re.DOTALL)
    text, count = pattern.subn("", text)
    if count != 1:
        raise ValueError(f"Expected one asciitilde_at lookup, found {count}")
    return text


def main() -> None:
    glyphs_path = Path(os.environ.get("FIRACODE_GLYPHS_FILE", "FiraCode.glyphs"))
    requested = sys.argv[1:]
    unsupported = sorted(set(requested) - FEATURE_MAPPINGS.keys())
    if unsupported:
        raise SystemExit(
            "Default-glyph baking is not implemented for: " + ", ".join(unsupported)
        )

    mappings = [mapping for feature in requested for mapping in FEATURE_MAPPINGS[feature]]
    text = glyphs_path.read_text()
    text = replace_layers(text, mappings)
    if "ss05" in requested:
        text = remove_tilde_at_lookup(text)
    glyphs_path.write_text(text)


if __name__ == "__main__":
    main()
