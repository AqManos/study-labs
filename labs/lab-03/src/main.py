"""Точка входа приложения «Дневник тренировок»."""

from __future__ import annotations

from stats import (
    build_summary,
    format_duration,
    longest_workout,
    most_common_kind,
    total_minutes,
)
from storage import load_workouts, save_workouts
from ui import (
    InputCancelled,
    print_menu,
    print_table,
    read_date,
    read_duration,
    read_int,
    read_line,
    read_text,
)
from workout import (
    Workout,
    add_workout,
    delete_workout,
    find_workouts,
    sort_workouts,
)


def show_all(workouts: list[Workout]) -> None:
    """Показать все тренировки, сверху новые."""
    print("\n=== Все тренировки ===")
    print_workouts(sort_workouts(workouts))


def print_workouts(workouts: list[Workout]) -> None:
    if not workouts:
        print("Записей нет.")
        return

    rows = []
    for workout in workouts:
        note = workout.note
        if len(note) > 40:
            note = note[:37] + "..."
        rows.append(
            [
                str(workout.id),
                workout.date,
                workout.kind,
                str(workout.duration),
                note or "-",
            ]
        )

    print_table(["ID", "Дата", "Вид", "Минуты", "Заметка"], rows)
    print(f"Всего записей: {len(workouts)}.")


def add_new(workouts: list[Workout]) -> None:
    """Добавить тренировку и сразу сохранить файл."""
    print("\nНовая тренировка. Для отмены нажмите Ctrl+C.")
    workout_date = read_date("Дата (2026-11-21 или 21.11.2026): ")
    kind = read_text("Вид тренировки: ")
    duration = read_duration("Длительность в минутах: ")
    note = read_text("Заметка (необязательно): ", required=False)

    workout = add_workout(workouts, workout_date, kind, duration, note)
    ok, message = save_workouts(workouts)

    print(
        f"Добавлена тренировка #{workout.id}: "
        f"{workout.kind}, {workout.date}, {format_duration(workout.duration)}."
    )
    print(message)
    if not ok:
        print("Данные остались в памяти. Попробуйте сохранить ещё раз через пункт 6.")


def search(workouts: list[Workout]) -> None:
    """Найти тренировки по виду, дате или заметке."""
    query = read_text("Что искать (вид, дата или заметка): ")
    found = sort_workouts(find_workouts(workouts, query))

    print("\n=== Результаты поиска ===")
    print_workouts(found)


def remove(workouts: list[Workout]) -> None:
    """Удалить тренировку по ID."""
    if not workouts:
        print("Удалять пока нечего.")
        return

    print("\n=== Удаление тренировки ===")
    print_workouts(sort_workouts(workouts))

    workout_id = read_int("ID тренировки для удаления: ", 1, 1_000_000_000)
    removed = delete_workout(workouts, workout_id)
    if removed is None:
        print(f"Тренировка с ID {workout_id} не найдена.")
        return

    ok, message = save_workouts(workouts)
    print(f"Удалена тренировка #{removed.id}: {removed.kind}, {removed.date}.")
    print(message)
    if not ok:
        print("Данные остались в памяти. Попробуйте сохранить ещё раз через пункт 6.")


def show_stats(workouts: list[Workout]) -> None:
    """Показать общую статистику и разбивку по видам тренировок."""
    if not workouts:
        print("Пока нет тренировок, статистику считать не по чему.")
        return

    summary = build_summary(workouts)
    total = total_minutes(workouts)
    average = round(total / len(workouts))

    print("\n=== Статистика ===")
    print(f"Всего тренировок: {len(workouts)}.")
    print(f"Суммарное время: {format_duration(total)}.")
    print(f"Средняя длительность: {format_duration(average)}.")

    longest = longest_workout(workouts)
    if longest is not None:
        print(
            f"Самая длинная: {longest.kind}, "
            f"{format_duration(longest.duration)}, {longest.date}."
        )

    popular = most_common_kind(summary)
    if popular is not None:
        print(f"Чаще всего: {popular.kind}, повторов: {popular.count}.")

    ordered = sorted(
        summary.values(),
        key=lambda value: (-value.total_minutes, value.kind),
    )
    rows = []
    for item in ordered:
        rows.append(
            [
                item.kind,
                str(item.count),
                format_duration(item.total_minutes),
                format_duration(round(item.average_minutes)),
            ]
        )

    print("\nПо видам:")
    print_table(["Вид", "Кол-во", "Всего", "Среднее"], rows)


def save_now(workouts: list[Workout]) -> None:
    """Сохранить данные по команде пользователя."""
    ok, message = save_workouts(workouts)
    print(message)
    if not ok:
        print("Проверьте права на запись в папку data.")


def menu_loop(workouts: list[Workout]) -> None:
    """Главное меню приложения."""
    actions = {
        "1": show_all,
        "2": add_new,
        "3": search,
        "4": remove,
        "5": show_stats,
        "6": save_now,
    }

    while True:
        print_menu()
        choice = read_line("Выберите пункт: ").strip()

        if choice == "0":
            return

        action = actions.get(choice)
        if action is None:
            print("Нет такого пункта меню.")
            continue

        action(workouts)


def main() -> int:
    workouts, messages = load_workouts()
    for message in messages:
        print(message)
    print(f"Загружено тренировок: {len(workouts)}.")

    exit_code = 0
    try:
        menu_loop(workouts)
    except InputCancelled:
        print("Ввод прерван.")
    finally:
        ok, message = save_workouts(workouts)
        print(message)
        if not ok:
            exit_code = 1

    print("До встречи.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
