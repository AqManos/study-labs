"""Ввод с клавиатуры и вывод таблиц."""

from __future__ import annotations

from datetime import date as date_type
from datetime import datetime


DATE_FORMATS = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y")


class InputCancelled(Exception):
    """Пользователь прервал ввод через Ctrl+C или Ctrl+D."""


def read_line(prompt: str) -> str:
    """Прочитать строку. При прерывании ввода поднять InputCancelled."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt) as exc:
        print()
        raise InputCancelled from exc


def read_text(prompt: str, required: bool = True) -> str:
    """Прочитать непустую строку. Если required=False, пустая строка допустима."""
    while True:
        value = read_line(prompt).strip()
        if value:
            return value
        if not required:
            return ""
        print("Пустая строка не подходит. Введите значение.")


def read_int(prompt: str, minimum: int, maximum: int) -> int:
    """Прочитать целое число в заданном диапазоне."""
    while True:
        raw = read_line(prompt).strip()
        if not raw:
            print("Введите число.")
            continue
        try:
            value = int(raw)
        except ValueError:
            print("Это не целое число. Попробуйте ещё раз.")
            continue
        if not minimum <= value <= maximum:
            print(f"Нужно число от {minimum} до {maximum}.")
            continue
        return value


def parse_date(raw: str) -> date_type | None:
    """Разобрать дату в одном из поддерживаемых форматов."""
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(raw, date_format).date()
        except ValueError:
            continue
    return None


def read_date(prompt: str) -> str:
    """Прочитать дату и вернуть её в формате ГГГГ-ММ-ДД."""
    while True:
        raw = read_line(prompt).strip()
        parsed = parse_date(raw)
        if parsed is None:
            print("Не понял дату. Примеры: 2026-11-21 или 21.11.2026.")
            continue
        if parsed > date_type.today():
            print("Дата не может быть в будущем.")
            continue
        return parsed.isoformat()


def read_duration(prompt: str) -> int:
    """Прочитать длительность тренировки в минутах."""
    return read_int(prompt, 1, 24 * 60)


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    """Напечатать простую таблицу с выравниванием по ширине колонок."""
    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    header_line = "  ".join(
        headers[index].ljust(widths[index]) for index in range(len(headers))
    )
    print(header_line)
    print("  ".join("-" * width for width in widths))
    for row in rows:
        row_line = "  ".join(
            row[index].ljust(widths[index]) for index in range(len(headers))
        )
        print(row_line)


def print_menu() -> None:
    print("\n=== Дневник тренировок ===")
    print("1. Показать все тренировки")
    print("2. Добавить тренировку")
    print("3. Найти тренировки")
    print("4. Удалить тренировку")
    print("5. Статистика")
    print("6. Сохранить сейчас")
    print("0. Выход")
