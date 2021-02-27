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
        self._final_state = {claim['station_code']: claim['zone'] for claim in self._territory_claims}

    def calculate_scores(self):
        tla_to_territories = {}

        for territory in self._final_state:
            if self._final_state[territory] not in tla_to_territories:
                tla_to_territories[self._final_state[territory]] = []
            tla_to_territories[self._final_state[territory]].append(territory)

        return {
            tla: sum([POINTS_PER_TERRITORY for territory in tla_to_territories.get(zone, [])])
            for zone, tla in self._zone_to_tla.items()
        }


if __name__ == '__main__':
    import libproton
    libproton.main(Scorer)
