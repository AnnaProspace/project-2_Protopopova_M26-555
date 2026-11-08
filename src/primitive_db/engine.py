"""Command loop for the database."""

import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import ID_COLUMN, META_FILE
from primitive_db.core import (
    column_type,
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.parser import coerce, parse_clause, split_values
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def _starts(text, prefix):
    """Return True when text begins with prefix, ignoring case."""
    return text.lower().startswith(prefix.lower())


def _split_once(text, separator):
    """Split text on the first case-insensitive separator."""
    lowered = text.lower()
    index = lowered.find(separator.lower())
    if index < 0:
        return None
    left = text[:index]
    right = text[index + len(separator):]
    return left, right


def _one_word(text):
    """Return a single table name, or None."""
    name = text.strip()
    if not name or " " in name:
        return None
    return name


def print_help():
    """Prints the help message for the current mode."""
    print("\n***Операции с данными***")
    print("\nФункции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = "
        "<значение> - прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = "
        "<новое_значение1> where <столбец_условия> = "
        "<значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = "
        "<значение> - удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("<command> exit - выход из программы")
    print("<command> help- справочная информация\n")


def _bad_value(value):
    """Print a validation message for a bad argument."""
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def _require_table(metadata, table_name):
    """Return False and print an error when the table is missing."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    return True


def _parse_where(metadata, table_name, text):
    """Parse a where clause into a one-item dictionary."""
    try:
        column, raw = parse_clause(text)
    except ValueError:
        _bad_value(text)
        return None
    type_name = column_type(metadata, table_name, column)
    if type_name is None:
        _bad_value(column)
        return None
    try:
        value = coerce(raw, type_name)
    except ValueError:
        _bad_value(raw)
        return None
    return {column: value}


def _print_rows(metadata, table_name, rows):
    """Print rows with PrettyTable."""
    columns = [item.split(":", 1)[0] for item in metadata[table_name]]
    table = PrettyTable()
    table.field_names = columns
    for row in rows:
        table.add_row([row.get(name, "") for name in columns])
    print(table)


def _handle_table_command(metadata, user_input):
    """Handle create_table, list_tables and drop_table."""
    try:
        args = shlex.split(user_input)
    except ValueError:
        _bad_value(user_input)
        return
    command, *rest = args
    if command == "list_tables":
        if rest:
            _bad_value(rest[0])
        else:
            list_tables(metadata)
        return
    if command == "create_table":
        if len(rest) < 2:
            _bad_value(rest[0] if rest else command)
            return
        updated = create_table(metadata, rest[0], rest[1:])
        if updated is not None:
            save_metadata(META_FILE, updated)
        return
    if command == "drop_table":
        if len(rest) != 1:
            _bad_value(rest[0] if rest else command)
            return
        updated = drop_table(metadata, rest[0])
        if updated is not None:
            save_metadata(META_FILE, updated)
            delete_table_data(rest[0])


def _handle_insert(metadata, user_input):
    """Insert one row into a table."""
    text = user_input.strip()
    if not _starts(text, "insert into "):
        _bad_value(user_input)
        return
    rest = text[len("insert into "):]
    parts = _split_once(rest, " values")
    if parts is None:
        _bad_value(user_input)
        return
    table_name = _one_word(parts[0])
    values_part = parts[1].strip()
    has_parens = values_part.startswith("(") and values_part.endswith(")")
    if table_name is None or not has_parens:
        _bad_value(user_input)
        return
    if not _require_table(metadata, table_name):
        return
    try:
        values = split_values(values_part[1:-1])
    except ValueError:
        _bad_value(values_part)
        return
    updated = insert(metadata, table_name, values)
    if updated is not None:
        save_table_data(table_name, updated)


def _handle_select(metadata, user_input):
    """Print all rows or rows matched by where."""
    text = user_input.strip()
    if not _starts(text, "select from "):
        _bad_value(user_input)
        return
    rest = text[len("select from "):]
    where_parts = _split_once(rest, " where ")
    if where_parts is None:
        table_name = _one_word(rest)
        where_text = None
    else:
        table_name = _one_word(where_parts[0])
        where_text = where_parts[1].strip()
    if table_name is None:
        _bad_value(user_input)
        return
    if not _require_table(metadata, table_name):
        return
    where_clause = None
    if where_text is not None:
        where_clause = _parse_where(metadata, table_name, where_text)
        if where_clause is None:
            return
    rows = select(load_table_data(table_name), where_clause)
    _print_rows(metadata, table_name, rows)


def _handle_update(metadata, user_input):
    """Update rows matched by where."""
    text = user_input.strip()
    if not _starts(text, "update "):
        _bad_value(user_input)
        return
    rest = text[len("update "):]
    set_parts = _split_once(rest, " set ")
    if set_parts is None:
        _bad_value(user_input)
        return
    table_name = _one_word(set_parts[0])
    where_parts = _split_once(set_parts[1], " where ")
    if table_name is None or where_parts is None:
        _bad_value(user_input)
        return
    set_text = where_parts[0].strip()
    where_text = where_parts[1].strip()
    if not _require_table(metadata, table_name):
        return
    try:
        set_column, set_raw = parse_clause(set_text)
    except ValueError:
        _bad_value(set_text)
        return
    if set_column.upper() == ID_COLUMN:
        _bad_value(set_column)
        return
    set_type = column_type(metadata, table_name, set_column)
    if set_type is None:
        _bad_value(set_column)
        return
    try:
        set_value = coerce(set_raw, set_type)
    except ValueError:
        _bad_value(set_raw)
        return
    where_clause = _parse_where(metadata, table_name, where_text)
    if where_clause is None:
        return
    data = load_table_data(table_name)
    matched = select(data, where_clause)
    if not matched:
        print("Ошибка: Записи не найдены.")
        return
    update(data, {set_column: set_value}, where_clause)
    save_table_data(table_name, data)
    for row in matched:
        print(
            f'Запись с ID={row[ID_COLUMN]} в таблице "{table_name}" '
            "успешно обновлена."
        )


def _handle_delete(metadata, user_input):
    """Delete rows matched by where after confirmation."""
    text = user_input.strip()
    if not _starts(text, "delete from "):
        _bad_value(user_input)
        return
    rest = text[len("delete from "):]
    where_parts = _split_once(rest, " where ")
    if where_parts is None:
        _bad_value(user_input)
        return
    table_name = _one_word(where_parts[0])
    where_text = where_parts[1].strip()
    if table_name is None:
        _bad_value(user_input)
        return
    if not _require_table(metadata, table_name):
        return
    where_clause = _parse_where(metadata, table_name, where_text)
    if where_clause is None:
        return
    data = load_table_data(table_name)
    matched = select(data, where_clause)
    if not matched:
        print("Ошибка: Записи не найдены.")
        return
    updated = delete(data, where_clause)
    if updated is None:
        return
    save_table_data(table_name, updated)
    for row in matched:
        print(
            f'Запись с ID={row[ID_COLUMN]} успешно удалена '
            f'из таблицы "{table_name}".'
        )


def _handle_info(metadata, user_input):
    """Print a table schema and the number of rows."""
    text = user_input.strip()
    if not _starts(text, "info "):
        _bad_value(user_input)
        return
    table_name = _one_word(text[len("info "):])
    if table_name is None:
        _bad_value(user_input)
        return
    if not _require_table(metadata, table_name):
        return
    columns = ", ".join(metadata[table_name])
    count = len(load_table_data(table_name))
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns}")
    print(f"Количество записей: {count}")


def run():
    """Run the database command loop."""
    print_help()
    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(">>> Введите команду: ")
        stripped = user_input.strip()
        if not stripped:
            continue
        head = stripped.split(maxsplit=1)[0].lower()
        if head == "exit":
            break
        if head == "help":
            print_help()
        elif head in {"create_table", "list_tables", "drop_table"}:
            _handle_table_command(metadata, stripped)
        elif head == "insert":
            _handle_insert(metadata, stripped)
        elif head == "select":
            _handle_select(metadata, stripped)
        elif head == "update":
            _handle_update(metadata, stripped)
        elif head == "delete":
            _handle_delete(metadata, stripped)
        elif head == "info":
            _handle_info(metadata, stripped)
        else:
            print(f"Функции {head} нет. Попробуйте снова.")
