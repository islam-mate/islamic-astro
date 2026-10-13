# islamic-astro 🌙

**Pure Python zero-dependency astronomical calculations for Islamic prayer times, Qibla direction, and solar positions.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## ✨ Features
- 🚀 **Zero Dependencies**: Pure standard library only (`math`, `datetime`, `zoneinfo`).
- 🕌 **7 Calculation Methods**: MWL, ISNA, Egypt, Umm al-Qura (Makkah), Karachi, Tehran, Jafari.
- 📐 **Asr Juristic Methods**: Standard (Shafi'i, Maliki, Hanbali) & Hanafi.
- 🧭 **High-Precision Qibla**: Great-circle bearing and distance (km) to Holy Kaaba.
- ⏳ **Next Prayer Tracking**: Remaining time with automatic next-day Fajr rollover.
- 🌙 **Ramadan Fasting Calendar**: Suhoor & Iftar schedules.
- 💻 **Built-in CLI**: Run calculations directly from your terminal.

---

## 📦 Installation
```bash
pip install islamic-astro
```

---

## 🚀 Quick Start

### 1. Calculate Daily Prayer Times
```python
import datetime as dt
from islamic_astro import calculate_prayer_times, CalculationMethod

times = calculate_prayer_times(
    latitude=30.0444,
    longitude=31.2357,
    date=dt.date.today(),
    timezone="Africa/Cairo",
    method=CalculationMethod.EGYPT
)

print(times.fajr.strftime("%H:%M"))     # 05:28
print(times.dhuhr.strftime("%H:%M"))    # 12:41
print(times.asr.strftime("%H:%M"))      # 15:58
print(times.maghrib.strftime("%H:%M"))  # 18:26
print(times.isha.strftime("%H:%M"))     # 19:43

# Or serialize to JSON-ready dict in Arabic:
data = times.to_dict(lang="ar")
```

### 2. Calculate Qibla Direction
```python
from islamic_astro import calculate_qibla

qibla = calculate_qibla(latitude=30.0444, longitude=31.2357)

print(f"Angle: {qibla.bearing:.1f}°")          # 136.1° from True North
print(f"Direction: {qibla.direction}")         # SE
print(f"Distance: {qibla.distance_km:.0f} km") # 1287 km
```

### 3. Get Next Prayer
```python
from islamic_astro import get_next_prayer

next_prayer = get_next_prayer(latitude=30.0444, longitude=31.2357, timezone="Africa/Cairo")
print(f"Next: {next_prayer['name_en']} at {next_prayer['time']} ({next_prayer['remaining_minutes']}m left)")
```

### 4. Command Line Usage
```bash
# Prayer times for Cairo
python -m islamic_astro.cli prayer --lat 30.04 --lng 31.23 --tz Africa/Cairo

# Qibla bearing
python -m islamic_astro.cli qibla --lat 30.04 --lng 31.23

# Next prayer
python -m islamic_astro.cli next --lat 30.04 --lng 31.23
```

---

## 📄 License
MIT License.
