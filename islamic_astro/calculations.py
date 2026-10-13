"""
Astronomical Solar Position and Prayer Times Calculations.
Pure Python, zero-dependency mathematical and astronomical engine.
"""

import datetime as dt
import math
from typing import Callable, Tuple


def eot_decl(time: dt.datetime) -> Tuple[dt.timedelta, float]:
    """
    Calculate Equation of Time (EoT) and Solar Declination for a given UTC datetime.
    
    Returns:
        tuple[dt.timedelta, float]: (Equation of time as timedelta, Declination in radians)
    """
    utc = dt.timezone.utc
    if time.tzinfo is None:
        time = time.replace(tzinfo=utc)
    else:
        time = time.astimezone(utc)

    epoch = dt.datetime(2000, 1, 1, 12, tzinfo=utc)
    days_since_epoch = (time - epoch).total_seconds() / 86400.0
    y100 = days_since_epoch / 36525.0

    # Orbital eccentricity
    e = 1.6709e-2 - 4.193e-5 * y100 - 1.26e-7 * (y100 ** 2)
    # Longitude of perihelion
    lam_p = math.radians(282.93807 + 1.7195 * y100 + 3.025e-4 * (y100 ** 2))
    # Obliquity of the ecliptic
    epsilon = math.radians(23.4393 - 0.013 * y100 - 2e-7 * (y100 ** 2) + 5e-7 * (y100 ** 3))

    MD = 6.24004077
    TY = 365.2596358
    D = days_since_epoch % TY
    M = (MD + 2.0 * math.pi * D / TY) % (2.0 * math.pi)

    # Solve Kepler's equation for eccentric anomaly E
    E = kepler_solve(M, e)
    # True anomaly nu
    nu = math.acos((math.cos(E) - e) / (1.0 - e * math.cos(E)))
    if E > math.pi:
        nu = 2.0 * math.pi - nu

    # Ecliptic longitude of the Sun
    lam = (nu + lam_p) % (2.0 * math.pi)

    # Right ascension alpha
    if math.isclose(math.cos(lam), 0.0, abs_tol=1e-9):
        alpha = lam
    else:
        alpha = math.atan(math.cos(epsilon) * math.tan(lam))
        if lam < math.pi / 2.0:
            pass
        elif lam < math.pi * 1.5:
            alpha += math.pi
        else:
            alpha += 2.0 * math.pi

    # Equation of time in radians
    eot_rad = M + lam_p - alpha
    if eot_rad > math.pi:
        eot_rad -= 2.0 * math.pi
    elif eot_rad < -math.pi:
        eot_rad += 2.0 * math.pi

    eot_min = eot_rad / (2.0 * math.pi) * 1440.0
    eot = dt.timedelta(minutes=eot_min)

    # Declination
    decl = math.asin(math.sin(epsilon) * math.sin(lam))
    return eot, decl


def kepler_solve(M: float, e: float) -> float:
    """
    Solve Kepler's equation: M = E - e * sin(E) for eccentric anomaly E.
    Uses Newton-Raphson numerical method.
    """
    if not (0.0 < e < 1.0):
        raise ValueError("Eccentricity of elliptical orbit must be in range (0, 1)")

    E = M
    max_iter = 100
    for _ in range(max_iter):
        delta = (E - e * math.sin(E) - M) / (1.0 - e * math.cos(E))
        E -= delta
        if abs(delta) < 1e-9:
            break
    return E


def calc_altitude(shadow_factor: float, declination: float, latitude: float) -> float:
    """
    Calculate solar altitude angle for a specific shadow factor (used in Asr prayer).
    """
    phi = math.radians(latitude)
    delta = declination
    shadow_factor_zenith = abs(math.tan(phi - delta))
    return math.atan(1.0 / (shadow_factor + shadow_factor_zenith))


def timedelta_at_altitude(altitude: float, declination: float, latitude: float) -> dt.timedelta:
    """
    Calculate the time delta from solar noon when the Sun reaches a given altitude.
    """
    alpha = altitude
    phi = math.radians(latitude)
    delta = declination

    numerator = math.sin(alpha) - math.sin(phi) * math.sin(delta)
    denominator = math.cos(phi) * math.cos(delta)

    if math.isclose(denominator, 0.0, abs_tol=1e-9):
        raise ValueError("Sun does not reach altitude at this latitude")

    cos_hour_rad = numerator / denominator
    if cos_hour_rad < -1.0 or cos_hour_rad > 1.0:
        raise ValueError("Sun does not reach the specified altitude on this date and latitude")

    hour_rad = math.acos(cos_hour_rad)
    hours = (hour_rad / (2.0 * math.pi)) * 24.0
    return dt.timedelta(hours=hours)


def linear_interpolation(
    diff_function: Callable[[dt.datetime], dt.timedelta],
    guess1: dt.datetime,
    guess2: dt.datetime,
    tolerance_seconds: float = 0.5,
    max_iter: int = 50
) -> dt.datetime:
    """
    Root finding using the secant method for precise solar time determination.
    """
    if abs((guess1 - guess2).total_seconds()) < 1e-6:
        raise ValueError("guess1 and guess2 must be different")

    if guess2 < guess1:
        guess1, guess2 = guess2, guess1

    diff1 = diff_function(guess1)
    diff2 = diff_function(guess2)

    for _ in range(max_iter):
        sec_diff = (diff2 - diff1).total_seconds()
        if abs(sec_diff) < 1e-9:
            break
        step = diff1.total_seconds() * ((guess2 - guess1).total_seconds() / sec_diff)
        guess3 = guess1 - dt.timedelta(seconds=step)
        diff3 = diff_function(guess3)

        if abs((guess3 - guess2).total_seconds()) < tolerance_seconds:
            return guess3

        guess1, diff1 = guess2, diff2
        guess2, diff2 = guess3, diff3

    return guess2


def time_zenith(date: dt.date, longitude: float) -> dt.datetime:
    """
    Calculate solar noon (transit/zenith time) in UTC.
    """
    utc_noon = dt.datetime(date.year, date.month, date.day, 12, tzinfo=dt.timezone.utc)
    time_zenith_approx = utc_noon - dt.timedelta(hours=longitude / 15.0)

    def calc_difference(guess: dt.datetime) -> dt.timedelta:
        eot, _ = eot_decl(guess)
        actual = utc_noon - dt.timedelta(hours=longitude / 15.0) - eot
        return actual - guess

    guess1 = time_zenith_approx - dt.timedelta(minutes=20)
    guess2 = time_zenith_approx + dt.timedelta(minutes=20)
    return linear_interpolation(calc_difference, guess1, guess2)


def time_altitude(zenith: dt.datetime, altitude: float, latitude: float, rising: bool) -> dt.datetime:
    """
    Calculate the time the Sun reaches a given altitude (rising for Fajr/Sunrise, setting for Maghrib/Isha).
    """
    def calc_difference(guess: dt.datetime) -> dt.timedelta:
        _, declination = eot_decl(guess)
        T = timedelta_at_altitude(altitude, declination, latitude)
        actual = (zenith - T) if rising else (zenith + T)
        return actual - guess

    if rising:
        guess1 = zenith - dt.timedelta(hours=12)
        guess2 = zenith
    else:
        guess1 = zenith
        guess2 = zenith + dt.timedelta(hours=12)

    return linear_interpolation(calc_difference, guess1, guess2)


def time_shadow_factor(zenith: dt.datetime, shadow_factor: float, latitude: float, rising: bool = False) -> dt.datetime:
    """
    Calculate the time corresponding to a shadow length factor (used for Asr).
    """
    def calc_difference(guess: dt.datetime) -> dt.timedelta:
        _, declination = eot_decl(guess)
        altitude = calc_altitude(shadow_factor, declination, latitude)
        T = timedelta_at_altitude(altitude, declination, latitude)
        actual = (zenith - T) if rising else (zenith + T)
        return actual - guess

    if rising:
        guess1 = zenith - dt.timedelta(hours=12)
        guess2 = zenith
    else:
        guess1 = zenith
        guess2 = zenith + dt.timedelta(hours=12)

    return linear_interpolation(calc_difference, guess1, guess2)
