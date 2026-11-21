"""Чтение и запись дневника тренировок в JSON."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from workout import Workout


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "workouts.json"


def load_workouts(path: Path = DATA_PATH) -> tuple[list[Workout], list[str]]:
    """Загрузить тренировки из файла.

    Возвращает список записей и список сообщений о проблемах. Если файла нет,
    возвращается пустой список: программа должна запускаться и без данных.
    """
    if not path.exists():
        return [], [f"Файл {path.name} не найден. Начинаю с пустого дневника."]

    try:
        raw_text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        backup_message = _make_backup(path)
        return [], [f"Файл {path.name} не в UTF-8: {exc}. {backup_message}"]
    except OSError as exc:
        return [], [f"Не удалось прочитать {path.name}: {exc}"]

    if not raw_text.strip():
        return [], []

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        backup_message = _make_backup(path)
        return [], [f"Файл {path.name} повреждён: {exc.msg}. {backup_message}"]

    if not isinstance(data, list):
        backup_message = _make_backup(path)
        return [], [f"Ожидался JSON-массив. {backup_message}"]

    workouts: list[Workout] = []
    messages: list[str] = []
    used_ids: set[int] = set()

    for index, item in enumerate(data, start=1):
        try:
            workout = Workout.from_dict(item)
        except ValueError as exc:
            messages.append(f"Запись {index} пропущена: {exc}.")
            continue

        if workout.id in used_ids:
            messages.append(
                f"Запись {index} пропущена: ID {workout.id} уже используется."
            )
            continue

        used_ids.add(workout.id)
        workouts.append(workout)

    return workouts, messages


def save_workouts(workouts: list[Workout], path: Path = DATA_PATH) -> tuple[bool, str]:
    """Сохранить тренировки в файл. Вернуть признак успеха и сообщение."""
    temp_path = path.with_name(path.name + ".tmp")

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temp_path.open("w", encoding="utf-8", newline="\n") as file:
            json.dump(
                [workout.to_dict() for workout in workouts],
                file,
                ensure_ascii=False,
                indent=2,
            )
            file.write("\n")
        temp_path.replace(path)
    except OSError as exc:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        return False, f"Не удалось сохранить данные: {exc}"

    return True, f"Сохранено записей: {len(workouts)}."


def _make_backup(path: Path) -> str:
    """Сохранить копию повреждённого файла рядом с оригиналом."""
    backup_path = path.with_name(path.name + ".bak")
    try:
        shutil.copy2(path, backup_path)
    except OSError as exc:
        return f"Копию создать не удалось: {exc}."
    return f"Копия сохранена в {backup_path.name}."
