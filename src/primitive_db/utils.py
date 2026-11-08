import json
from pathlib import Path


def load_metadata(filepath):
    """Load table metadata from a JSON file."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Save table metadata to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def _table_path(table_name):
    return Path("data") / f"{table_name}.json"


def load_table_data(table_name):
    """Load rows of one table. Missing file means an empty table."""
    path = _table_path(table_name)
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Save rows of one table."""
    path = _table_path(table_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def delete_table_data(table_name):
    """Remove the data file of a dropped table."""
    path = _table_path(table_name)
    if path.exists():
        path.unlink()
