"""
islamic-astro: Zero-dependency astronomical prayer times and Qibla calculations in pure Python.
"""

__version__ = "1.0.0"

from .calculations import (
    eot_decl,
    kepler_solve,
    time_zenith,
    time_altitude,
    time_shadow_factor,
)
from .methods import (
    CalculationMethod,
    AsrMethod,
    GeneralMethod,
    get_method_calculator,
)
from .prayer import (
    PrayerTimesResult,
    calculate_prayer_times,
    get_next_prayer,
    get_monthly_schedule,
    PRAYER_NAMES,
)
from .qibla import (
    QiblaResult,
    calculate_qibla,
    calculate_bearing,
    calculate_distance,
    bearing_to_direction,
)
from .ramadan import (
    RamadanDay,
    get_ramadan_calendar,
)

__all__ = [
    "CalculationMethod",
    "AsrMethod",
    "GeneralMethod",
    "get_method_calculator",
    "PrayerTimesResult",
    "calculate_prayer_times",
    "get_next_prayer",
    "get_monthly_schedule",
    "PRAYER_NAMES",
    "QiblaResult",
    "calculate_qibla",
    "calculate_bearing",
    "calculate_distance",
    "bearing_to_direction",
    "RamadanDay",
    "get_ramadan_calendar",
]
