import functools
import time


def handle_db_errors(func):
    """Print database errors instead of stopping the program."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
            return None
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
            return None
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
            return None
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
            return None

    return wrapper


def confirm_action(action_name):
    """Ask for confirmation before a dangerous operation."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Print how long the function ran."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        started = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - started
            print(
                f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд."
            )

    return wrapper


def create_cacher():
    """Return a closure that stores results by key."""
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    return cache_result
