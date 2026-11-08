"""Parsers for values and where/set clauses."""

from primitive_db.constants import TYPE_BOOL, TYPE_INT, TYPE_STR


def _is_identifier(text):
    """Return True when text is a column or table name."""
    if not text:
        return False
    first = text[0]
    if not (first.isalpha() or first == "_"):
        return False
    for char in text[1:]:
        if not (char.isalnum() or char == "_"):
            return False
    return True


def _is_int(text):
    """Return True when text is an integer literal."""
    digits = text[1:] if text.startswith("-") else text
    return bool(digits) and digits.isdigit()


def coerce(raw, expected_type):
    """Convert a command literal to the column type."""
    text = raw.strip()
    if expected_type == TYPE_STR:
        if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
            return text[1:-1]
        raise ValueError(text)
    if expected_type == TYPE_INT:
        if _is_int(text):
            return int(text)
        raise ValueError(text)
    if expected_type == TYPE_BOOL:
        lowered = text.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        raise ValueError(text)
    raise ValueError(text)


def parse_clause(text):
    """Turn 'age = 28' into a column name and a raw value."""
    cleaned = text.strip()
    if "=" not in cleaned:
        raise ValueError(cleaned)
    column, raw = cleaned.split("=", 1)
    column = column.strip()
    raw = raw.strip()
    if not _is_identifier(column) or not raw:
        raise ValueError(cleaned)
    return column, raw


def split_values(raw):
    """Split insert values, keeping quotes around strings."""
    parts = []
    buf = []
    quote = None
    for char in raw:
        if quote:
            buf.append(char)
            if char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
            buf.append(char)
        elif char == ",":
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(char)
    if quote:
        raise ValueError(raw)
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts
