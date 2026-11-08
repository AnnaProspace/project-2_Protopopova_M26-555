import shlex

import prompt

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

METADATA_FILE = "db_meta.json"


def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> "
        ".. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def _bad_value(value):
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def run():
    """Run the table-management loop."""
    print_help()
    while True:
        metadata = load_metadata(METADATA_FILE)
        user_input = prompt.string(">>>Введите команду: ")
        try:
            args = shlex.split(user_input)
        except ValueError:
            _bad_value(user_input)
            continue
        if not args:
            continue

        command, *rest = args
        if command == "exit":
            break
        if command == "help":
            print_help()
        elif command == "list_tables":
            if rest:
                _bad_value(rest[0])
            else:
                list_tables(metadata)
        elif command == "create_table":
            if len(rest) < 2:
                _bad_value(rest[0] if rest else command)
                continue
            updated = create_table(metadata, rest[0], rest[1:])
            if updated is not None:
                save_metadata(METADATA_FILE, updated)
        elif command == "drop_table":
            if len(rest) != 1:
                _bad_value(rest[0] if rest else command)
                continue
            updated = drop_table(metadata, rest[0])
            if updated is not None:
                save_metadata(METADATA_FILE, updated)
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
