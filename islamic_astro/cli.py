"""
CLI entry point for islamic-astro.
"""

import argparse
import sys
from .prayer import calculate_prayer_times, get_next_prayer
from .qibla import calculate_qibla
from .methods import CalculationMethod


def main():
    parser = argparse.ArgumentParser(
        prog="islamic-astro",
        description="Calculate Islamic prayer times and Qibla direction from the command line."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Prayer times command
    prayer_parser = subparsers.add_parser("prayer", help="Calculate daily prayer times")
    prayer_parser.add_argument("--lat", type=float, required=True, help="Latitude (-90 to 90)")
    prayer_parser.add_argument("--lng", type=float, required=True, help="Longitude (-180 to 180)")
    prayer_parser.add_argument("--tz", type=str, default="Africa/Cairo", help="Timezone (e.g. UTC, Europe/London)")
    prayer_parser.add_argument("--method", type=str, default="EGYPT", help="Calculation method")
    prayer_parser.add_argument("--date", type=str, default=None, help="YYYY-MM-DD (default: today)")
    prayer_parser.add_argument("--lang", type=str, choices=["en", "ar"], default="en", help="Output language")

    # Qibla command
    qibla_parser = subparsers.add_parser("qibla", help="Calculate Qibla direction and distance")
    qibla_parser.add_argument("--lat", type=float, required=True, help="Latitude (-90 to 90)")
    qibla_parser.add_argument("--lng", type=float, required=True, help="Longitude (-180 to 180)")
    qibla_parser.add_argument("--lang", type=str, choices=["en", "ar"], default="en", help="Output language")

    # Next prayer command
    next_parser = subparsers.add_parser("next", help="Find upcoming prayer")
    next_parser.add_argument("--lat", type=float, required=True, help="Latitude (-90 to 90)")
    next_parser.add_argument("--lng", type=float, required=True, help="Longitude (-180 to 180)")
    next_parser.add_argument("--tz", type=str, default="Africa/Cairo", help="Timezone")

    args = parser.parse_args()

    if args.command == "prayer":
        res = calculate_prayer_times(args.lat, args.lng, date=args.date, timezone=args.tz, method=args.method)
        data = res.to_dict(lang=args.lang)
        print(f"\nPrayer Times for {data['date']} ({args.lat}, {args.lng}) [Method: {args.method}]:")
        print(f"Sunrise : {data['sunrise']}")
        for p in data["prayers"]:
            print(f"{p['name']:<10}: {p['time']}")

    elif args.command == "qibla":
        res = calculate_qibla(args.lat, args.lng)
        data = res.to_dict(lang=args.lang)
        print(f"\nQibla Information:")
        print(f"Bearing     : {data['bearing']}° from True North")
        print(f"Direction   : {data['direction']}")
        print(f"Distance    : {data['distance_km']:,} km")
        print(f"Description : {data['description']}")

    elif args.command == "next":
        res = get_next_prayer(args.lat, args.lng, timezone=args.tz)
        print(f"\nNext Prayer: {res['name_en']} ({res['name_ar']}) at {res['time']}")
        print(f"Time Remaining: {res['remaining_minutes']} minutes ({res['remaining_seconds']} seconds)")
        if res["is_tomorrow"]:
            print("(Note: This is tomorrow's Fajr)")


if __name__ == "__main__":
    main()
