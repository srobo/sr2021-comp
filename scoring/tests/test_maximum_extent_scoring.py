#!/usr/bin/env python3

import unittest

import yaml

# Path hackery
import pathlib
import sys
ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from score import MaximumExtentScorer as Scorer


class ScorerTests(unittest.TestCase):
    longMessage = True

    def construct_scorer(self, territory_claims):
        return Scorer(
            self.teams_data,
            {'other': {'territory_claims': territory_claims}},
        )

    def assertScores(self, expected_scores, territory_claims):
        scorer = self.construct_scorer(territory_claims)
        actual_scores = scorer.calculate_scores()

        self.assertEqual(expected_scores, actual_scores, "Wrong scores")

    def setUp(self):
        self.teams_data = {
            'ABC': {'zone': 0},
            'DEF': {'zone': 1},
        }

    def test_template(self):
        template_path = ROOT / 'template.yaml'
        with template_path.open() as f:
            data = yaml.load(f)

        teams_data = data['teams']
        arena_data = data.get('arena_zones')
        extra_data = data.get('other')

        scorer = Scorer(teams_data, arena_data)
        scores = scorer.calculate_scores()

        self.assertEqual(
            teams_data.keys(),
            scores.keys(),
            "Should return score values for every team",
        )

    def test_no_claims(self):
        self.assertScores({
            'ABC': 0,
            'DEF': 0,
        }, [])

    def test_single_claim(self):
        self.assertScores({
            'ABC': 2,
            'DEF': 0,
        }, [
            {
                'zone': 0,
                'station_code': 'PN',
                'time': 4.432
            }
        ])

    def test_two_claims_same_territory(self):
        self.assertScores({
            'ABC': 2,
            'DEF': 2,
        }, [
            {
                'zone': 0,
                'station_code': 'PN',
                'time': 4
            },
            {
                'zone': 1,
                'station_code': 'PN',
                'time': 5
            }
        ])

    def test_two_concurrent_territories(self):
        self.assertScores({
            'ABC': 4,
            'DEF': 2,
        }, [
            {
                'zone': 0,
                'station_code': 'PN',
                'time': 4
            },
            {
                'zone': 0,
                'station_code': 'EY',
                'time': 5
            },
            {
                'zone': 1,
                'station_code': 'PN',
                'time': 5.01
            }
        ])

    def test_two_isolated_territories(self):
        self.assertScores({
            'ABC': 2,
            'DEF': 2,
        }, [
            {
                'zone': 0,
                'station_code': 'PN',
                'time': 4
            },
            {
                'zone': 1,
                'station_code': 'PN',
                'time': 5
            },
            {
                'zone': 0,
                'station_code': 'EY',
                'time': 5.01
            }
        ])

    def test_both_teams_claim_both_territories(self):
        # But only one of them holds both at the same time
        self.assertScores({
            'ABC': 2,
            'DEF': 4,
        }, [
            {
                'zone': 0,
                'station_code': 'PN',
                'time': 4
            },
            {
                'zone': 1,
                'station_code': 'PN',
                'time': 5
            },
            {
                'zone': 1,
                'station_code': 'EY',
                'time': 6
            },
            {
                'zone': 0,
                'station_code': 'EY',
                'time': 7
            }
        ])

    def test_territory_becoming_unclaimed_after_it_was_claimed(self):
        self.assertScores({
            'ABC': 2,
            'DEF': 2,
        }, [
            {
                'zone': 0,
                'station_code': 'PN',
                'time': 4
            },
            {
                'zone': 1,
                'station_code': 'PN',
                'time': 5
            },
            {
                'zone': 0,
                'station_code': 'PN',
                'time': 6
            },
            {
                'zone': -1,
                'station_code': 'PN',
                'time': 7
            },
        ])

    def test_unclaimed_territory_with_others_claimed(self):
        self.assertScores({
            'ABC': 4,
            'DEF': 2,
        }, [
            {
                'zone': 0,
                'station_code': 'PN',
                'time': 4
            },
            {
                'zone': 1,
                'station_code': 'PN',
                'time': 5
            },
            {
                'zone': 0,
                'station_code': 'PN',
                'time': 6
            },
            {
                'zone': 0,
                'station_code': 'EY',
                'time': 7
            },
            {
                'zone': -1,
                'station_code': 'PN',
                'time': 8
            },
            {
                'zone': 1,
                'station_code': 'SZ',
                'time': 9
            },
        ])

if __name__ == '__main__':
    unittest.main()
