"""Статистика по тренировкам."""

from __future__ import annotations

from dataclasses import dataclass

from workout import Workout


@dataclass
class KindSummary:
    """Итоги по одному виду тренировок."""

    kind: str
    count: int = 0
    total_minutes: int = 0

    @property
    def average_minutes(self) -> float:
        if self.count == 0:
            return 0.0
        return self.total_minutes / self.count


def build_summary(workouts: list[Workout]) -> dict[str, KindSummary]:
    """Сгруппировать тренировки по виду через словарь."""
    summary: dict[str, KindSummary] = {}

    for workout in workouts:
        item = summary.get(workout.kind)
        if item is None:
            item = KindSummary(kind=workout.kind)
            summary[workout.kind] = item
        item.count += 1
        item.total_minutes += workout.duration

    return summary


def total_minutes(workouts: list[Workout]) -> int:
    """Суммарная длительность всех тренировок."""
    return sum(workout.duration for workout in workouts)


def format_duration(minutes: int) -> str:
    """Показать минуты в удобном виде: 90 -> 1 ч 30 мин."""
    hours, rest = divmod(minutes, 60)
    if hours and rest:
        return f"{hours} ч {rest} мин"
    if hours:
        return f"{hours} ч"
    return f"{rest} мин"


def longest_workout(workouts: list[Workout]) -> Workout | None:
    """Самая длинная тренировка."""
    if not workouts:
        return None
    return max(workouts, key=lambda workout: (workout.duration, workout.date))


def most_common_kind(summary: dict[str, KindSummary]) -> KindSummary | None:
    """Вид тренировок, который встречается чаще всего."""
    if not summary:
        return None
    return max(summary.values(), key=lambda item: (item.count, item.total_minutes))
