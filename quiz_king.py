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


class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()

    def __call__(self, doc):
        # TODO: need to remove punctuations if it requires
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]


class MorphyStemmer:
    def __init__(self):
        self.tokenizer = TreebankWordTokenizer()

    def __call__(self, doc):
        stemmed_doc = []
        for t in self.tokenizer.tokenize(doc):
            stem = wordnet.morphy(t)
            if stem:
                stemmed_doc.append(stem.lower())
            else:
                stemmed_doc.append(t.lower())
        return stemmed_doc


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
    q_train_set = train_set.get_field('Question Text')
    q_test_set = test_set.get_field('Question Text')
    # vectorizer = TfidfVectorizer(stop_words='english')
    vectorizer = TfidfVectorizer(stop_words='english',
                                 ngram_range=(1, 2),
                                 use_idf=True,
                                 tokenizer=MorphyStemmer())
    vectors = vectorizer.fit_transform(q_train_set+q_test_set).todense()
    q_train_set = vectors[:len(q_train_set)]
    q_test_set = vectors[len(q_train_set):]
    ans_train_set = train_set.get_field('Answer')

    print ">>> Benchmark..."
    train_bench, test_bench = train_set.train_test_split()
    test_bench_q = [ii['Question Text'] for ii in test_bench]
    test_bench_a = [ii['Answer'] for ii in test_bench]
    train_bench_q = [ii['Question Text'] for ii in train_bench]
    train_bench_a = [ii['Answer'] for ii in train_bench]
    vectors_bench = vectorizer.fit_transform(train_bench_q+test_bench_q).todense()
    train_bench_q = vectors_bench[:len(train_bench_q)]
    test_bench_q = vectors_bench[len(train_bench_q):]

    clf_bench = GaussianNB()
    clf_bench.fit(train_bench_q, train_bench_a)
    right = 0
    total = len(test_bench_q)
    print "Number of benchmark: ", total
    for idx, ii in enumerate(test_bench_q):
        prediction = clf_bench.predict(ii)[0]
        print test_bench_a[idx] == prediction, test_bench_a[idx], prediction
        if prediction == test_bench_a[idx]:
            right += 1
    print("Accuracy on dev: %f" % (float(right) / float(total)))

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
