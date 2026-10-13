"""
Unit tests for islamic_astro calculations, methods, and Qibla.
Uses standard library unittest.
"""

import unittest
import datetime as dt
from islamic_astro import (
    calculate_prayer_times,
    get_next_prayer,
    calculate_qibla,
    CalculationMethod,
    AsrMethod,
    get_monthly_schedule,
)


class TestIslamicAstro(unittest.TestCase):

    def test_prayer_times_cairo(self):
        lat = 30.0444
        lng = 31.2357
        test_date = dt.date(2026, 1, 15)

        res = calculate_prayer_times(
            latitude=lat,
            longitude=lng,
            date=test_date,
            timezone="Africa/Cairo",
            method=CalculationMethod.EGYPT
        )

        self.assertEqual(res.date, test_date)
        self.assertEqual(res.latitude, lat)
        self.assertEqual(res.longitude, lng)

        # Check times chronological order
        self.assertTrue(res.fajr < res.sunrise < res.dhuhr < res.asr < res.maghrib < res.isha)

        # Serialization
        d = res.to_dict(lang="ar")
        self.assertEqual(len(d["prayers"]), 5)
        self.assertEqual(d["prayers"][0]["name"], "الفجر")

    def test_prayer_times_all_methods(self):
        lat, lng = 24.7136, 46.6753  # Riyadh
        test_date = dt.date(2026, 6, 21)

        for method in CalculationMethod:
            res = calculate_prayer_times(lat, lng, date=test_date, timezone="Asia/Riyadh", method=method)
            self.assertTrue(res.fajr < res.sunrise < res.dhuhr < res.asr < res.maghrib < res.isha)

    def test_hanafi_asr(self):
        lat, lng = 30.0444, 31.2357
        test_date = dt.date(2026, 3, 21)

        standard = calculate_prayer_times(lat, lng, test_date, method="MWL", asr=AsrMethod.STANDARD)
        hanafi = calculate_prayer_times(lat, lng, test_date, method="MWL", asr=AsrMethod.HANAFI)

        # Hanafi Asr is later than Standard Asr (shadow factor 2 vs 1)
        self.assertTrue(hanafi.asr > standard.asr)

    def test_qibla_cairo(self):
        lat = 30.0444
        lng = 31.2357
        qibla = calculate_qibla(lat, lng)

        self.assertTrue(130.0 <= qibla.bearing <= 140.0)
        self.assertEqual(qibla.direction, "SE")
        self.assertTrue(1200.0 <= qibla.distance_km <= 1400.0)

    def test_next_prayer(self):
        lat, lng = 30.0444, 31.2357
        next_p = get_next_prayer(lat, lng, timezone="Africa/Cairo")
        self.assertIn("key", next_p)
        self.assertTrue(next_p["remaining_seconds"] >= 0)
        self.assertIn("time", next_p)

    def test_monthly_schedule(self):
        lat, lng = 30.0444, 31.2357
        schedule = get_monthly_schedule(lat, lng, 2026, 2)
        # February 2026 has 28 days
        self.assertEqual(len(schedule), 28)


if __name__ == "__main__":
    unittest.main()
