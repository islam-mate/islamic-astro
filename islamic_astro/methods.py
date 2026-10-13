"""
Calculation methods and astronomical parameters for Islamic prayer times.
"""

from enum import Enum, auto, unique
import datetime as dt
import math
from typing import Dict, Union

from .calculations import time_zenith, time_altitude, time_shadow_factor


@unique
class CalculationMethod(Enum):
    """Recognized Islamic astronomical calculation conventions."""
    EGYPT = auto()      # Egyptian General Authority of Survey
    MWL = auto()        # Muslim World League
    ISNA = auto()       # Islamic Society of North America
    MAKKAH = auto()     # Umm al-Qura University, Makkah
    KARACHI = auto()    # University of Islamic Sciences, Karachi
    TEHRAN = auto()     # Institute of Geophysics, University of Tehran
    JAFARI = auto()     # Shia Ithna Ashari (Leva Institute, Qum)

    @classmethod
    def from_str(cls, name: str) -> "CalculationMethod":
        key = name.strip().upper()
        if hasattr(cls, key):
            return getattr(cls, key)
        raise ValueError(f"Unknown calculation method '{name}'. Choose from: {[m.name for m in cls]}")


@unique
class AsrMethod(Enum):
    """School of thought for Asr shadow factor."""
    STANDARD = auto()   # Majority (Shafi'i, Maliki, Hanbali) - shadow factor 1
    HANAFI = auto()     # Hanafi school - shadow factor 2

    @classmethod
    def from_str(cls, name: str) -> "AsrMethod":
        key = name.strip().upper()
        if hasattr(cls, key):
            return getattr(cls, key)
        raise ValueError(f"Unknown Asr method '{name}'. Choose from: STANDARD, HANAFI")


class GeneralMethod:
    """General base calculation method with custom angles."""

    def __init__(
        self,
        fajr_altitude_deg: float,
        isha_altitude_deg: float,
        asr_method: AsrMethod = AsrMethod.STANDARD
    ):
        self.asr_method = asr_method
        self.shadow_factor = 2.0 if asr_method == AsrMethod.HANAFI else 1.0
        self.fajr_altitude = -math.radians(fajr_altitude_deg)
        self.isha_altitude = -math.radians(isha_altitude_deg)
        self.sunset_altitude = -math.radians(0.833)  # Standard atmospheric refraction & solar disc

    def calc_times(
        self,
        date: dt.date,
        timezone: dt.tzinfo,
        longitude: float,
        latitude: float,
        is_ramadan: bool = False
    ) -> Dict[str, dt.datetime]:
        """
        Calculate solar prayer times for the given date and coordinates.
        """
        zenith = time_zenith(date, longitude)
        fajr = time_altitude(zenith, self.fajr_altitude, latitude, rising=True)
        sunrise = time_altitude(zenith, self.sunset_altitude, latitude, rising=True)
        asr = time_shadow_factor(zenith, self.shadow_factor, latitude, rising=False)
        maghrib = time_altitude(zenith, self.sunset_altitude, latitude, rising=False)
        isha = time_altitude(zenith, self.isha_altitude, latitude, rising=False)

        times = {
            "fajr": fajr.astimezone(timezone),
            "sunrise": sunrise.astimezone(timezone),
            "dhuhr": zenith.astimezone(timezone),
            "asr": asr.astimezone(timezone),
            "maghrib": maghrib.astimezone(timezone),
            "isha": isha.astimezone(timezone),
        }
        return times


class TehranMethod(GeneralMethod):
    """Tehran University: Maghrib at -4.5 deg, Fajr 17.7, Isha 14."""
    def __init__(self, asr_method: AsrMethod = AsrMethod.STANDARD):
        super().__init__(17.7, 14.0, asr_method=asr_method)

    def calc_times(self, date: dt.date, timezone: dt.tzinfo, longitude: float, latitude: float, is_ramadan: bool = False):
        times = super().calc_times(date, timezone, longitude, latitude, is_ramadan)
        zenith = time_zenith(date, longitude)
        times["maghrib"] = time_altitude(zenith, -math.radians(4.5), latitude, rising=False).astimezone(timezone)
        return times


class JafariMethod(GeneralMethod):
    """Jafari / Shia Leva: Fajr 16, Isha 14, Maghrib -4.0 deg."""
    def __init__(self, asr_method: AsrMethod = AsrMethod.STANDARD):
        super().__init__(16.0, 14.0, asr_method=asr_method)

    def calc_times(self, date: dt.date, timezone: dt.tzinfo, longitude: float, latitude: float, is_ramadan: bool = False):
        times = super().calc_times(date, timezone, longitude, latitude, is_ramadan)
        zenith = time_zenith(date, longitude)
        times["maghrib"] = time_altitude(zenith, -math.radians(4.0), latitude, rising=False).astimezone(timezone)
        return times


class MakkahMethod(GeneralMethod):
    """Umm Al-Qura (Makkah): Fajr 18.5 deg, Isha fixed 90 min after Maghrib (120 min in Ramadan)."""
    def __init__(self, asr_method: AsrMethod = AsrMethod.STANDARD):
        super().__init__(18.5, 18.5, asr_method=asr_method)

    def calc_times(self, date: dt.date, timezone: dt.tzinfo, longitude: float, latitude: float, is_ramadan: bool = False):
        times = super().calc_times(date, timezone, longitude, latitude, is_ramadan)
        offset_minutes = 120 if is_ramadan else 90
        times["isha"] = times["maghrib"] + dt.timedelta(minutes=offset_minutes)
        return times


def get_method_calculator(
    method: Union[CalculationMethod, str] = CalculationMethod.MWL,
    asr: Union[AsrMethod, str] = AsrMethod.STANDARD
) -> GeneralMethod:
    """Factory helper to obtain the calculation method handler."""
    if isinstance(method, str):
        method = CalculationMethod.from_str(method)
    if isinstance(asr, str):
        asr = AsrMethod.from_str(asr)

    if method == CalculationMethod.ISNA:
        return GeneralMethod(15.0, 15.0, asr)
    elif method == CalculationMethod.MWL:
        return GeneralMethod(18.0, 17.0, asr)
    elif method == CalculationMethod.EGYPT:
        return GeneralMethod(19.5, 17.5, asr)
    elif method == CalculationMethod.KARACHI:
        return GeneralMethod(18.0, 18.0, asr)
    elif method == CalculationMethod.TEHRAN:
        return TehranMethod(asr)
    elif method == CalculationMethod.JAFARI:
        return JafariMethod(asr)
    elif method == CalculationMethod.MAKKAH:
        return MakkahMethod(asr)
    else:
        raise ValueError(f"Unsupported calculation method {method}")
