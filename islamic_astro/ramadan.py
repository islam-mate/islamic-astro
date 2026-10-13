"""
Ramadan schedule and fasting time calculations.
"""

from dataclasses import dataclass
import datetime as dt
from typing import Dict, List, Optional, Union

from .prayer import calculate_prayer_times, PrayerTimesResult
from .methods import CalculationMethod, AsrMethod


@dataclass
class RamadanDay:
    day_number: int
    date: dt.date
    suhoor_end: str     # Fajr time
    sunrise: str
    dhuhr: str
    asr: str
    iftar: str          # Maghrib time
    isha: str
    fasting_duration: str


def get_ramadan_calendar(
    latitude: float,
    longitude: float,
    start_date: dt.date,
    total_days: int = 30,
    timezone: str = "Africa/Cairo",
    method: Union[CalculationMethod, str] = CalculationMethod.EGYPT,
    asr: Union[AsrMethod, str] = AsrMethod.STANDARD
) -> List[RamadanDay]:
    """
    Generate complete 29 or 30-day Ramadan fasting schedule.
    """
    calendar_days = []
    for day in range(1, total_days + 1):
        cur_date = start_date + dt.timedelta(days=day - 1)
        pt = calculate_prayer_times(latitude, longitude, cur_date, timezone, method, asr, is_ramadan=True)

        fasting_seconds = (pt.maghrib - pt.fajr).total_seconds()
        hours = int(fasting_seconds // 3600)
        minutes = int((fasting_seconds % 3600) // 60)
        duration_str = f"{hours}h {minutes}m"

        calendar_days.append(
            RamadanDay(
                day_number=day,
                date=cur_date,
                suhoor_end=pt.fajr.strftime("%H:%M"),
                sunrise=pt.sunrise.strftime("%H:%M"),
                dhuhr=pt.dhuhr.strftime("%H:%M"),
                asr=pt.asr.strftime("%H:%M"),
                iftar=pt.maghrib.strftime("%H:%M"),
                isha=pt.isha.strftime("%H:%M"),
                fasting_duration=duration_str
            )
        )
    return calendar_days
