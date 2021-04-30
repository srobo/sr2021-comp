#!/usr/bin/env python3

import argparse
import sys
from operator import itemgetter

import matplotlib.pyplot as plt
import numpy as np
from colour import Color
from sr.comp.comp import SRComp

comp = SRComp('.')

def game_point_by_match(tla):
    for (_, num), points in {**comp.scores.league.game_points, **comp.scores.knockout.game_points}.items():
        if tla in points:
            yield num, points[tla]
        else:
            yield num, 0


def plot(final_match_num, tlas, highlight, output):
    if tlas is None:
        tlas = [team.tla for team in comp.teams.values()]

    if highlight is None:
        highlight = tlas

    hues = np.linspace(0.,1.,len(tlas))
    fig, ax = plt.subplots()
    final_val_order = []
    i = 0
    teams = [team for team in comp.teams.values() if team.tla in tlas]

    for team in teams:
        if not team.is_still_around(final_match_num):
            continue

        line_colour = Color(hsl=(hues[i], 1., 0.5))
        z_order = 10
        if team.tla not in highlight:
            line_colour.luminance = 0.9
            z_order = 0

        score_list = sorted(game_point_by_match(team.tla))

        score_only = [score for (_,score) in score_list]

        score_cum = 0
        score_cum_list = []
        for score in score_only:
            score_cum += score
            score_cum_list.append(score_cum)

        ax.plot(score_cum_list, label=team.tla, color=line_colour.hex, zorder=z_order)
        final_val_order.append((score_cum, i))
        i += 1

    final_val_order.sort()
    final_val_order.reverse()
    order = [i for (_, i) in final_val_order]
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(
        [handles[idx] for idx in order],
        [labels[idx] for idx in order],
        loc=2,
    )
    plt.xlabel("Matches")
    plt.ylabel("Game Points")
    plt.savefig(output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--final-match-num', help='Exclude Teams not present at this match number', type=int, default=144)
    parser.add_argument('--teams', help='list of TLAs of teams to plot', nargs='+')
    parser.add_argument('--highlight', help='list of TLAs of teams to highlight in plot', nargs='+')
    parser.add_argument('--output', required=True, help='Where to save the plot')

    args = parser.parse_args()

    plot(args.final_match_num, args.teams, args.highlight, args.output)
