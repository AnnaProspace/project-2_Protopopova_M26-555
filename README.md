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
## CRUD-операции

Команда `database` работает с записями. Строки лежат в `data/<имя_таблицы>.json`. В `insert` поле `ID` не передаётся.

```text
insert into users values ("Sergei", 28, true)
select from users where age = 28
update users set age = 29 where name = "Sergei"
delete from users where ID = 1
info users
```
## Демонстрация CRUD

[![asciicast](https://asciinema.org/a/OOd5wf7xC7LGhR2d.svg)](https://asciinema.org/a/OOd5wf7xC7LGhR2d)
## Декораторы

Ошибки файлов, отсутствующих таблиц и неверных типов перехватывает `handle_db_errors`.

`drop_table` и `delete` спрашивают подтверждение. Операция выполняется только после ответа `y`. Любой другой ответ её отменяет.

`insert` и `select` печатают время выполнения. Повтор одинакового `select` берётся из кэша.
## Демонстрация декораторов

[![asciicast](https://asciinema.org/a/PzckFWPVvUagXNOK.svg)](https://asciinema.org/a/PzckFWPVvUagXNOK)