from primitive_db.parser import coerce
from primitive_db.utils import load_table_data

VALID_TYPES = ("int", "str", "bool")


def create_table(metadata, table_name, columns):
    """Create a table and return updated metadata, or None on error."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None

    parsed = []
    for column in columns:
        if column.count(":") != 1:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return None
        name, type_name = column.split(":", 1)
        if not name or type_name not in VALID_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return None
        parsed.append((name, type_name))

    if not any(name.upper() == "ID" for name, _type_name in parsed):
        parsed.insert(0, ("ID", "int"))

    metadata[table_name] = [f"{name}:{type_name}" for name, type_name in parsed]
    rendered = ", ".join(metadata[table_name])
    print(f'Таблица "{table_name}" успешно создана со столбцами: {rendered}')
    return metadata


def drop_table(metadata, table_name):
    """Delete a table and return updated metadata, or None on error."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Print all table names."""
    if not metadata:
        print("Таблиц нет.")
        return
    for name in metadata:
        print(f"- {name}")


def column_type(metadata, table_name, column_name):
    """Return the declared type of a column, or None."""
    for item in metadata[table_name]:
        name, type_name = item.split(":", 1)
        if name == column_name:
            return type_name
    return None


def _schema(metadata, table_name):
    return [item.split(":", 1) for item in metadata[table_name]]


def insert(metadata, table_name, values):
    """Insert a row. ID is generated. Returns all rows, or None."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    data_columns = [
        (name, type_name)
        for name, type_name in _schema(metadata, table_name)
        if name.upper() != "ID"
    ]
    if len(values) != len(data_columns):
        print("Некорректное значение: количество значений. Попробуйте снова.")
        return None

    record = {}
    for (name, type_name), raw in zip(data_columns, values, strict=True):
        try:
            record[name] = coerce(raw, type_name)
        except ValueError:
            print(f"Некорректное значение: {raw}. Попробуйте снова.")
            return None

    data = load_table_data(table_name)
    ids = [row["ID"] for row in data if isinstance(row, dict) and "ID" in row]
    new_id = max(ids) + 1 if ids else 1
    stored = {"ID": new_id}
    stored.update(record)
    data.append(stored)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return data


def select(table_data, where_clause=None):
    """Return all rows, or only rows that match where_clause."""
    if where_clause is None:
        return list(table_data)
    return [
        row
        for row in table_data
        if all(row.get(key) == value for key, value in where_clause.items())
    ]


def update(table_data, set_clause, where_clause):
    """Update matching rows and return the full row list."""
    for row in table_data:
        if all(row.get(key) == value for key, value in where_clause.items()):
            row.update(set_clause)
    return table_data


def delete(table_data, where_clause):
    """Return rows that do not match where_clause."""
    return [
        row
        for row in table_data
        if not all(row.get(key) == value for key, value in where_clause.items())
    ]
