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
