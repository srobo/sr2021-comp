import collections

POINTS_PER_TERRITORY = 2


class Scorer(object):
    # Assumption: we will trust the *ordering* of the entries in the data we
    # are given and *ignore* the actual 'time' values. We defer handling of
    # equialent-time operations to the territory controller.

    def __init__(self, teams_data, arena_data):
        self._zone_to_tla = {
            info['zone']: tla
            for tla, info in teams_data.items()
        }

        self._territory_claims = arena_data['other']['territory_claims']

        # Mapping from station_code -> owning zone
        self._territory_ownership = {}

    def _determine_max_extents(self, current_best):
        extents = collections.Counter(self._territory_ownership.values())

        return {
            zone: max(
                extents.get(zone, 0),
                current_best.get(zone, 0),
            )
            for zone in self._zone_to_tla.keys()
        }

    def calculate_scores(self):
        max_extents = {}

        for claim in self._territory_claims:
            code = claim['station_code']
            self._territory_ownership[code] = claim['zone']

            max_extents = self._determine_max_extents(max_extents)

        return {
            tla: max_extents.get(zone, 0) * POINTS_PER_TERRITORY
            for zone, tla in self._zone_to_tla.items()
        }


if __name__ == '__main__':
    import libproton
    libproton.main(Scorer)
