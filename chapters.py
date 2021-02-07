#!/usr/bin/env python3

import argparse
import datetime
from pathlib import Path

from sr.comp.comp import SRComp
from sr.comp.match_period import Match


def format_time(delta: datetime.timedelta) -> str:
    seconds = int(delta.total_seconds() // 1 % 60)
    minutes = int((delta.total_seconds() // 60) % 60)
    hours = int(delta.total_seconds() // (60 * 60))

    return f'{hours}:{minutes:0>2}:{seconds:0>2}'


def main(args: argparse.Namespace) -> None:
    offset = datetime.timedelta(seconds=args.offset_seconds)
    match_number: int = args.match_number

    comp = SRComp(Path(__file__).parent)

    if len(comp.arenas) != 1:
        raise ValueError("Multiple arenas not supported")

    if len(comp.corners) != 2:
        raise ValueError("More than two corners not supported")

    arena, = comp.arenas.keys()

    slots = comp.schedule.matches[match_number:]
    matches = [x[arena] for x in slots]

    # Yes, this doesn't account for the game not aligning within the slot.
    # Happily we don't need to account for that explicitly as it's a fixed
    # offset which affects all matches equally and thus drops out.
    stream_start = matches[0].start_time - offset

    print(f"{format_time(datetime.timedelta())} Introduction")
    for match in matches:
        if None in match.teams:
            print(
                f"Match {match.display_name} contains unknown teams. Stopping.",
                file=sys.stderr,
            )
            break

        match_steam_time = format_time(match.start_time - stream_start)
        teams = " vs ".join(match.teams)
        print(f"{match_steam_time} {match.display_name}: {teams}")

    print("Note: also add the outtro/wrapup!", file=sys.stderr)

import sys

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'offset_seconds',
        type=int,
        help=(
            "The YouTube url for the start of the first match. Hint: pause at "
            "the start of the match, then use 'Copy video URL at current time' "
            "and extract the value of the 't' argument from the query string."
        ),
    )
    parser.add_argument(
        'match_number',
        type=int,
        help="The match number to start at.",
    )
    return parser.parse_args()


if __name__ == '__main__':
    main(parse_args())
