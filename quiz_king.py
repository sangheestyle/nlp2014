import csv
from collections import defaultdict


class Corpus:
    """
    Store corpus
    """
    def __init__(self):
        self._corpus = None
        self._read = False
        self._type_scores = ['IR_Wiki Scores', 'QANTA Scores']

    def __len__(self):
        return len(self._corpus)

    def __iter__(self):
        assert self._read, "Corpus is empty"

        for ii in self._corpus:
            yield ii

    def read(self, path):
        with open(path, "rb") as f:
            self._corpus = list(csv.DictReader(f))
        for ii in self._corpus:
            for score_type in self._type_scores:
                ii[score_type] = self.form_dict(ii[score_type])
        self._read = True

    @staticmethod
    def form_dict(vals):
        d = defaultdict(float)
        for jj in vals.split(", "):
            key, val = jj.split(":")
            d[key.strip()] = float(val)
        return d


if __name__ == "__main__":
    import sys
    import os

    path = sys.argv[1]
    assert os.path.exists(path), "Path is wrong: %r" % path
    test_set = Corpus()
    test_set.read(path)
    print list(test_set)[0]
    print len(test_set)
