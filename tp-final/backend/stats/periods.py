"""Períodos de meses de calendario y agrupaciones por usuario y semana."""
import calendar
from collections import defaultdict
from datetime import date, timedelta

from backend.stats.core import SetRecord


def month_start(day: date) -> date:
    return day.replace(day=1)


def month_end(day: date) -> date:
    return day.replace(day=calendar.monthrange(day.year, day.month)[1])


def shift_months(day: date, months: int) -> date:
    index = day.year * 12 + day.month - 1 + months
    return date(index // 12, index % 12 + 1, 1)


def parse_month(text: str) -> date:
    try:
        year, month = (int(part) for part in text.split("-"))
        return date(year, month, 1)
    except (ValueError, AttributeError) as err:
        raise ValueError(f"Mes inválido: {text!r}; usá YYYY-MM") from err


def period_range(kind: str, today: date, month: str | None = None, start: str | None = None,
                 end: str | None = None, first: date | None = None) -> tuple[date, date]:
    current = month_start(today)
    if kind == "month":
        chosen = parse_month(month) if month else current
        return chosen, month_end(chosen)
    if kind in ("6m", "12m"):
        return shift_months(current, -5 if kind == "6m" else -11), month_end(current)
    if kind == "all":
        return month_start(first) if first else current, month_end(current)
    if kind == "custom":
        if not start or not end:
            raise ValueError("Un período a mano necesita desde y hasta")
        low, high = parse_month(start), parse_month(end)
        if low > high:
            raise ValueError("El período empieza después de terminar")
        return low, month_end(high)
    raise ValueError(f"Período desconocido: {kind!r}")


def in_range(records: list[SetRecord], start: date, end: date) -> list[SetRecord]:
    return [r for r in records if start <= r.date <= end]


def by_user(records: list[SetRecord]) -> dict[int, list[SetRecord]]:
    grouped: dict[int, list[SetRecord]] = defaultdict(list)
    for record in records:
        grouped[record.user_id].append(record)
    return grouped
