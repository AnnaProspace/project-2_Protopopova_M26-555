"""Decorators and a closure cache for database operations."""

import time

from primitive_db.constants import YES_ANSWER


def _keep_name(wrapper, func):
    """Copy the original function name and docstring."""
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def handle_db_errors(func):
    """Print database errors instead of stopping the program."""

    def wrapper(*args, **kwargs):
        """Run the function and translate database errors."""
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

    return _keep_name(wrapper, func)


def confirm_action(action_name):
    """Ask for confirmation before a dangerous operation."""

    def decorator(func):
        """Attach the confirmation prompt to a function."""

        def wrapper(*args, **kwargs):
            """Run the function only after the answer y."""
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer != YES_ANSWER:
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return _keep_name(wrapper, func)

    return decorator


def log_time(func):
    """Print how long the function ran."""

    def wrapper(*args, **kwargs):
        """Measure the call with time.monotonic."""
        started = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - started
            print(
                f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд."
            )

    return _keep_name(wrapper, func)


def create_cacher():
    """Return a closure that stores results by key."""
    cache = {}

    def cache_result(key, value_func):
        """Return a cached value or compute and store it."""
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    return cache_result
