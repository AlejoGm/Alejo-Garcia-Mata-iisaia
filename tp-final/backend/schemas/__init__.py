"""Modelos de entrada y salida de la API, por recurso."""
from backend.schemas.common import (
    Name30, ConfigOut, ProfileInput, ProfileOut, Name40, ExerciseInput, ExerciseOut, Person, PeriodOut,
)
from backend.schemas.groups import (
    GroupInput, GroupSummary, MemberOut, GroupDetail, ChallengesInput,
)
from backend.schemas.sessions import (
    SetInput, SessionInput, SetOut, SessionOut, LastSet, TargetOut, LastOut,
)
from backend.schemas.rankings import (
    StrengthRow, StrengthExercise, ProgressRow, WeeklyRow, ConsistencyRow, RankingsOut, ReactionKind, ReactionInput,
    FeedItem,
)
from backend.schemas.routines import (
    RoutineItemInput, RoutineDayInput, RoutineInput, RoutineItemOut, RoutineDayOut, RoutineOut, FollowInput,
)
from backend.schemas.competition import (
    DuelInput, DuelOut, SuggestionOut, SuggestionsOut, CampaignInput, StandingRow, CampaignOut,
)
from backend.schemas.stats import (
    MonthPointOut, WeekPointOut, BodyweightPointOut, PersonalStatsOut, WeekActivityOut, DayActivityOut, LeaderOut,
    StreakOut, DashboardOut,
)
