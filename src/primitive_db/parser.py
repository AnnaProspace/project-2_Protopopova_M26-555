import re


def coerce(raw, expected_type):
    """Convert a command literal to the column type."""
    text = raw.strip()
    if expected_type == "str":
        if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
            return text[1:-1]
        raise ValueError(text)
    if expected_type == "int":
        if re.fullmatch(r"-?\d+", text):
            return int(text)
        raise ValueError(text)
    if expected_type == "bool":
        if text.lower() == "true":
            return True
        if text.lower() == "false":
            return False
        raise ValueError(text)
    raise ValueError(text)


def parse_clause(text):
    """Turn 'age = 28' into a column name and a raw value."""
    match = re.fullmatch(
        r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)",
        text.strip(),
    )
    if not match:
        raise ValueError(text.strip())
    return match.group(1), match.group(2).strip()


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
