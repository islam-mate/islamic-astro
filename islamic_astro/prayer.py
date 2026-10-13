"""
High-level user-facing prayer times calculator and data structures.
"""

from dataclasses import dataclass
import datetime as dt
from typing import Dict, List, Optional, Union
from zoneinfo import ZoneInfo

from .methods import CalculationMethod, AsrMethod, get_method_calculator


PRAYER_NAMES = {
    "fajr": {"en": "Fajr", "ar": "الفجر"},
    "sunrise": {"en": "Sunrise", "ar": "الشروق"},
    "dhuhr": {"en": "Dhuhr", "ar": "الظهر"},
    "asr": {"en": "Asr", "ar": "العصر"},
    "maghrib": {"en": "Maghrib", "ar": "المغرب"},
    "isha": {"en": "Isha", "ar": "العشاء"},
}


@dataclass(frozen=True)
class PrayerTimesResult:
    """Calculated prayer times container for a specific date and location."""
    date: dt.date
    fajr: dt.datetime
    sunrise: dt.datetime
    dhuhr: dt.datetime
    asr: dt.datetime
    maghrib: dt.datetime
    isha: dt.datetime
    timezone: str
    latitude: float
    longitude: float
    method: str

    def to_dict(self, time_format: str = "%H:%M", lang: str = "en") -> Dict[str, Union[str, float, dict, list]]:
        """Serialize times into a clean dictionary."""
        def name_of(key: str) -> str:
            return PRAYER_NAMES.get(key, {}).get(lang, key.capitalize())

        return {
            "date": self.date.isoformat(),
            "location": {"latitude": self.latitude, "longitude": self.longitude},
            "timezone": self.timezone,
            "method": self.method,
            "sunrise": self.sunrise.strftime(time_format),
            "prayers": [
                {"key": "fajr", "name": name_of("fajr"), "time": self.fajr.strftime(time_format)},
                {"key": "dhuhr", "name": name_of("dhuhr"), "time": self.dhuhr.strftime(time_format)},
                {"key": "asr", "name": name_of("asr"), "time": self.asr.strftime(time_format)},
                {"key": "maghrib", "name": name_of("maghrib"), "time": self.maghrib.strftime(time_format)},
                {"key": "isha", "name": name_of("isha"), "time": self.isha.strftime(time_format)},
            ]
        }

    def get_prayer_map(self) -> Dict[str, dt.datetime]:
        """Get mapping of 5 prayers (excluding sunrise) to their datetimes."""
        return {
            "fajr": self.fajr,
            "dhuhr": self.dhuhr,
            "asr": self.asr,
            "maghrib": self.maghrib,
            "isha": self.isha,
        }


def _resolve_tz(tz: Union[str, dt.tzinfo]) -> dt.tzinfo:
    if isinstance(tz, str):
        return ZoneInfo(tz)
    return tz


def calculate_prayer_times(
    latitude: float,
    longitude: float,
    date: Optional[Union[dt.date, str]] = None,
    timezone: Union[str, dt.tzinfo] = "Africa/Cairo",
    method: Union[CalculationMethod, str] = CalculationMethod.EGYPT,
    asr: Union[AsrMethod, str] = AsrMethod.STANDARD,
    is_ramadan: bool = False
) -> PrayerTimesResult:
    """
    Calculate prayer times for given coordinates and date.

    Args:
        latitude: Geographic latitude in degrees (-90 to +90)
        longitude: Geographic longitude in degrees (-180 to +180)
        date: Calculation date (defaults to today)
        timezone: Timezone string (e.g. 'Africa/Cairo') or dt.tzinfo object
        method: Calculation method (e.g. CalculationMethod.EGYPT, 'MWL', 'ISNA')
        asr: Asr shadow factor school (AsrMethod.STANDARD or AsrMethod.HANAFI)
        is_ramadan: Whether to apply Ramadan offset for Makkah method
    """
    if isinstance(date, str):
        target_date = dt.date.fromisoformat(date)
    elif date is None:
        target_date = dt.date.today()
    else:
        target_date = date

    tz_obj = _resolve_tz(timezone)
    tz_str = tz_obj.key if hasattr(tz_obj, "key") else str(timezone)

    calc = get_method_calculator(method, asr)
    times = calc.calc_times(target_date, tz_obj, longitude, latitude, is_ramadan=is_ramadan)

    method_name = method.name if isinstance(method, CalculationMethod) else str(method).upper()

    return PrayerTimesResult(
        date=target_date,
        fajr=times["fajr"],
        sunrise=times["sunrise"],
        dhuhr=times["dhuhr"],
        asr=times["asr"],
        maghrib=times["maghrib"],
        isha=times["isha"],
        timezone=tz_str,
        latitude=latitude,
        longitude=longitude,
        method=method_name
    )


def get_next_prayer(
    latitude: float,
    longitude: float,
    now: Optional[dt.datetime] = None,
    timezone: Union[str, dt.tzinfo] = "Africa/Cairo",
    method: Union[CalculationMethod, str] = CalculationMethod.EGYPT,
    asr: Union[AsrMethod, str] = AsrMethod.STANDARD
) -> Dict[str, Union[str, int]]:
    """
    Determine the upcoming next prayer and the time remaining.
    Automatically handles next-day Fajr rollover.
    """
    tz_obj = _resolve_tz(timezone)
    current_time = now.astimezone(tz_obj) if now else dt.datetime.now(tz_obj)
    today_date = current_time.date()

    today_prayers = calculate_prayer_times(latitude, longitude, today_date, tz_obj, method, asr)
    prayer_map = today_prayers.get_prayer_map()

    for prayer_key in ["fajr", "dhuhr", "asr", "maghrib", "isha"]:
        prayer_time = prayer_map[prayer_key]
        if prayer_time > current_time:
            remaining_seconds = int((prayer_time - current_time).total_seconds())
            return {
                "key": prayer_key,
                "name_en": PRAYER_NAMES[prayer_key]["en"],
                "name_ar": PRAYER_NAMES[prayer_key]["ar"],
                "time": prayer_time.strftime("%H:%M"),
                "remaining_minutes": remaining_seconds // 60,
                "remaining_seconds": remaining_seconds,
                "is_tomorrow": False
            }

    # If all prayers of today have passed, the next prayer is tomorrow's Fajr
    tomorrow_date = today_date + dt.timedelta(days=1)
    tomorrow_prayers = calculate_prayer_times(latitude, longitude, tomorrow_date, tz_obj, method, asr)
    fajr_tomorrow = tomorrow_prayers.fajr
    remaining_seconds = int((fajr_tomorrow - current_time).total_seconds())

    return {
        "key": "fajr",
        "name_en": PRAYER_NAMES["fajr"]["en"],
        "name_ar": PRAYER_NAMES["fajr"]["ar"],
        "time": fajr_tomorrow.strftime("%H:%M"),
        "remaining_minutes": remaining_seconds // 60,
        "remaining_seconds": remaining_seconds,
        "is_tomorrow": True
    }


def get_monthly_schedule(
    latitude: float,
    longitude: float,
    year: int,
    month: int,
    timezone: Union[str, dt.tzinfo] = "Africa/Cairo",
    method: Union[CalculationMethod, str] = CalculationMethod.EGYPT,
    asr: Union[AsrMethod, str] = AsrMethod.STANDARD
) -> List[PrayerTimesResult]:
    """Calculate daily prayer times for an entire Gregorian month."""
    import calendar
    _, days_in_month = calendar.monthrange(year, month)
    results = []
    for day in range(1, days_in_month + 1):
        d = dt.date(year, month, day)
        results.append(calculate_prayer_times(latitude, longitude, d, timezone, method, asr))
    return results
