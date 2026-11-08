## Управление таблицами

Команда `database` открывает цикл работы с таблицами. Метаданные хранятся в `db_meta.json`.

Поддерживаемые типы столбцов: `int`, `str`, `bool`. Столбец `ID:int` добавляется автоматически.

```text
database
create_table users name:str age:int is_active:bool
list_tables
drop_table users
exit
```
## Демонстрация

[![asciicast](https://asciinema.org/a/cQBN4Pzy6NBhUa8F.svg)](https://asciinema.org/a/cQBN4Pzy6NBhUa8F)