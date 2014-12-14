import csv
from collections import defaultdict
from random import sample

from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import wordnet


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

    @property
    def corpus(self):
        return self._corpus

    def read(self, path):
        with open(path, "rb") as f:
            self._corpus = list(csv.DictReader(f))
        for ii in self._corpus:
            for score_type in self._type_scores:
                ii[score_type] = self.form_dict(ii[score_type])
        self._read = True

    def get_field(self, field):
        return [ii[field] for ii in self._corpus]

    @staticmethod
    def form_dict(vals):
        d = defaultdict(float)
        for jj in vals.split(", "):
            key, val = jj.split(":")
            d[key.strip()] = float(val)
        return d

    def train_test_split(self, portion=0.020, random=False):
        num_test_set = int(len(self._corpus)*portion)
        if random:
            test_set = sample(self._corpus, num_test_set)
        else:
            test_set = [ii for ii in self._corpus
                        if int(ii['Question ID']) % 50 == 0]
            assert num_test_set <= len(test_set),\
                   "Given portion is too high: %r" % portion
            test_set = test_set[:num_test_set]
        test_qid = set(ii['Question ID'] for ii in test_set)
        train_set = [qq for qq in self._corpus
                     if qq['Question ID'] not in test_qid]
        return train_set, test_set
