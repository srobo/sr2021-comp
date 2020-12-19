class Scorer(object):
    # Assumption: we will trust the *ordering* of the entries in the data we
    # are given and *ignore* the actual 'time' values. We defer handling of
    # equialent-time operations to the territory controller.

    def __init__(self, teams_data, arena_data):
        self._teams_data = teams_data

    def calculate_scores(self):
        raise NotImplementedError


if __name__ == '__main__':
    import libproton
    libproton.main(Scorer)
