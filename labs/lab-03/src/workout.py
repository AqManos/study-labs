"""Модель тренировки и операции над списком записей."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as date_type
from datetime import datetime


@dataclass
class Workout:
    """Одна запись в дневнике тренировок."""

    id: int
    date: str
    kind: str
    duration: int
    note: str = ""

    def to_dict(self) -> dict:
        """Превратить запись в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "date": self.date,
            "kind": self.kind,
            "duration": self.duration,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, raw: object) -> "Workout":
        """Собрать запись из словаря и проверить поля."""
        if not isinstance(raw, dict):
            raise ValueError("запись должна быть объектом JSON")

        workout_id = _read_positive_int(raw.get("id"), "id")
        duration = _read_positive_int(raw.get("duration"), "duration")

        raw_date = raw.get("date")
        if not isinstance(raw_date, str):
            raise ValueError("поле date должно быть строкой")
        try:
            date_type.fromisoformat(raw_date)
        except ValueError as exc:
            raise ValueError(f"некорректная дата {raw_date!r}") from exc

        raw_kind = raw.get("kind")
        if not isinstance(raw_kind, str) or not raw_kind.strip():
            raise ValueError("поле kind не может быть пустым")

        raw_note = raw.get("note", "")
        if raw_note is None:
            raw_note = ""
        if not isinstance(raw_note, str):
            raise ValueError("поле note должно быть строкой")

        return cls(
            id=workout_id,
            date=raw_date,
            kind=normalize_kind(raw_kind),
            duration=duration,
            note=raw_note.strip(),
        )


def _read_positive_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"поле {field} должно быть целым числом")
    if value <= 0:
        raise ValueError(f"поле {field} должно быть больше нуля")
    return value


def normalize_kind(kind: str) -> str:
    """Убрать лишние пробелы и сделать первую букву заглавной."""
    return " ".join(kind.split()).capitalize()


def next_id(workouts: list[Workout]) -> int:
    """Следующий свободный идентификатор."""
    return max((workout.id for workout in workouts), default=0) + 1


def add_workout(
    workouts: list[Workout],
    workout_date: str,
    kind: str,
    duration: int,
    note: str = "",
) -> Workout:
    """Добавить тренировку в список и вернуть новую запись."""
    workout = Workout(
        id=next_id(workouts),
        date=workout_date,
        kind=normalize_kind(kind),
        duration=duration,
        note=note.strip(),
    )
    workouts.append(workout)
    return workout


def delete_workout(workouts: list[Workout], workout_id: int) -> Workout | None:
    """Удалить тренировку по ID. Вернуть удалённую запись или None."""
    for index, workout in enumerate(workouts):
        if workout.id == workout_id:
            return workouts.pop(index)
    return None


def find_workouts(workouts: list[Workout], query: str) -> list[Workout]:
    """Найти записи по виду, дате или тексту заметки."""
    needle = query.strip().casefold()
    if not needle:
        return list(workouts)

    iso_date = _to_iso_date(query.strip())
    found = []
    for workout in workouts:
        if (
            needle in workout.kind.casefold()
            or needle in workout.note.casefold()
            or needle in workout.date
            or workout.date == iso_date
        ):
            found.append(workout)
    return found


def _to_iso_date(raw: str) -> str | None:
    """Перевести дату из 21.11.2026 в 2026-11-21, если получится."""
    for date_format in ("%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, date_format).date().isoformat()
        except ValueError:
            continue
    return None


def sort_workouts(workouts: list[Workout], newest_first: bool = True) -> list[Workout]:
    """Отсортировать записи по дате. По умолчанию сверху новые."""
    return sorted(
        workouts,
        key=lambda workout: (workout.date, workout.id),
        reverse=newest_first,
    )
