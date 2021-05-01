#!/usr/bin/env python3

import argparse
import itertools
import math
import sys
from operator import itemgetter

import matplotlib.pyplot as plt
import numpy as np
from colour import Color
from sr.comp.comp import SRComp
from sr.comp.match_period import MatchType, Match

DPI = 150
SIZE_INCHES = (1920 / DPI, 1080 / DPI)

comp = SRComp('.')


def coprime(a, b):
    return math.gcd(a, b) == 1


def find_coprime(n):
    for a in range(3, math.ceil(math.sqrt(n))):
        if coprime(a, n):
            return a

    return 3


def nth_steps(items):
    """
    >>> nth_steps('ABCDEFG')
    ['A', 'F', 'D', 'B', 'G', 'E']
    """
    n = find_coprime(len(items))
    return list(itertools.islice(
        itertools.islice(
            itertools.cycle(items),
            None,
            None,
            n,
        ),
        len(items),
    ))



def game_point_by_period(tla, match_periods):
    for period in match_periods:
        total = 0
        for slot in period.matches:
            for match in slot.values():
                if tla in match.teams:
                    scores = getattr(comp.scores, match.type.value)
                    match_id = (match.arena, match.num)
                    try:
                        total += scores.game_points[match_id][tla]
                    except KeyError:
                        # not scored yet
                        pass
        yield total


def plot(final_match_num, tlas, highlight, output):
    if tlas is None:
        tlas = comp.teams.keys()

    if highlight is None:
        highlight = tlas

    # Add 1 to prevent overlap when only showing a small number of teams; due to
    # the circular nature of colour wheels.
    hues = nth_steps(nth_steps(nth_steps(np.linspace(0., 1., len(tlas) + 1))))

    fig, ax = plt.subplots()
    fig.set_size_inches(*SIZE_INCHES)

    i = 0

    teams = [
        team
        for team in comp.teams.values()
        if team.tla in tlas
        if team.is_still_around(final_match_num)
    ]

    match_periods = comp.schedule.match_periods[:-1]

    n_cols = len(teams) + 1
    width = 1 / n_cols
    offset = n_cols / 2
    cols = np.arange(len(match_periods))

    for idx, team in enumerate(teams, start=1):
        line_colour = Color(hsl=(hues[i], .85, 0.65))
        z_order = 10
        if team.tla not in highlight:
            line_colour.luminance = 0.9
            z_order = 0

        score_only = list(game_point_by_period(team.tla, match_periods))

        score_cum = 0
        score_cum_list = []
        for score in score_only:
            score_cum += score
            score_cum_list.append(score)

        ax.bar(
            cols + (idx - offset) * width,
            score_cum_list,
            width=width,
            label=team.tla,
            color=line_colour.hex,
            zorder=z_order,
        )
        i += 1

    plt.legend(loc=2)
    plt.xlabel("Period")
    plt.xticks(cols, [x.description for x in match_periods])
    plt.ylabel("Game Points")
    plt.savefig(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--final-match-num',
        help='Exclude Teams not present at this match number',
        type=int,
        default=144,
    )
    parser.add_argument(
        '--teams',
        help='list of TLAs of teams to plot',
        nargs='+',
    )
    parser.add_argument(
        '--highlight',
        help='list of TLAs of teams to highlight in plot',
        nargs='+',
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Where to save the plot',
    )

    args = parser.parse_args()

    plot(args.final_match_num, args.teams, args.highlight, args.output)
