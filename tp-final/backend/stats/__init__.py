"""Reglas de cálculo de Gym-bro. Funciones puras: no conocen la base ni HTTP (ver docs/spec.md)."""
from backend.stats.competition import (
    CAMPAIGN_POINTS, CampaignEntry, DuelResult, best_value, campaign_points, duel_result, imbalance,
)
from backend.stats.core import (
    DOTS_COEFFICIENTS, MAX_REPS_FOR_1RM, SetRecord, absolute_key, best_1rm, best_absolute, chronological_key,
    detect_prs, dots, estimate_1rm, set_dots,
)
from backend.stats.periods import (
    by_user, in_range, month_end, month_start, parse_month, period_range, shift_months,
)
from backend.stats.rankings import (
    ConsistencyEntry, ProgressEntry, StrengthEntry, WeeklyEntry, best_1rm_by_exercise, consistency_table,
    goal_in_force, monday, progress_table, progress_windows, strength_table, training_days, week_results,
    weekly_table,
)
from backend.stats.personal import (
    BodyweightPoint, MonthPoint, WeekPoint, bodyweight_series, monthly_series, weekly_series,
)
