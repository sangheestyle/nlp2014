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


if __name__ == "__main__":
    import sys
    import os
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import GaussianNB

    train_path = sys.argv[1]
    test_path = sys.argv[2]
    output_path = sys.argv[3]
    assert os.path.exists(train_path), "Path is wrong: %r" % train_path
    assert os.path.exists(test_path), "Path is wrong: %r" % test_path

    print ">>> Processing corpus for train and test set."
    train_set = Corpus()
    train_set.read(train_path)
    test_set = Corpus()
    test_set.read(test_path)

    print ">>> Vectorizing..."
    vectorizer = TfidfVectorizer(stop_words='english')
    q_train_set = train_set.get_field('Question Text')
    q_test_set = test_set.get_field('Question Text')
    vectors = vectorizer.fit_transform(q_train_set+q_test_set).todense()
    q_train_set = vectors[:len(q_train_set)]
    q_test_set = vectors[len(q_train_set):]
    ans_train_set = train_set.get_field('Answer')

    print ">>> Training classifier..."
    clf = GaussianNB()
    clf.fit(q_train_set, ans_train_set)

    assert len(q_test_set) == len(test_set), "Check number of train set"

    output_header = ['Question ID', 'Answer']
    num_test = len(test_set)

    print ">>> Asking answer..."
    with open(output_path, "wb") as out_file:
        o = csv.DictWriter(out_file, output_header)
        o.writeheader()
        total = len(train_set)
        for idx, qq in enumerate(q_test_set):
            q_id = test_set.corpus[idx]['Question ID']
            expected_answer = clf.predict(qq)[0]
            print str(idx+1) + "/" + str(num_test) + ": ", \
                  q_id, expected_answer
            o.writerow({output_header[0]: q_id,
                        output_header[1]: expected_answer})
