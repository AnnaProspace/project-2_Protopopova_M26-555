"""Helpers for reading and writing JSON files."""

import json
import os

from primitive_db.constants import DATA_DIR


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
    """Return the JSON path for one table."""
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name):
    """Load rows of one table. Missing file means an empty table."""
    path = _table_path(table_name)
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Save rows of one table."""
    path = _table_path(table_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def delete_table_data(table_name):
    """Remove the data file of a dropped table."""
    path = _table_path(table_name)
    if os.path.exists(path):
        os.remove(path)
