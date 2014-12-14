"""
For benchmarking
$ python benchmark.py csv/train.csv
"""

import sys
import os

from corpus import Corpus
from similar_to_this import SimilarToThis


train_path = sys.argv[1]

print ">>> Processing corpus for train and test set."
train_set = Corpus()
train_set.read(train_path)

print ">>> Benchmark..."
train_bench, test_bench = train_set.train_test_split()
test_bench_q = [ii['Question Text'] for ii in test_bench]
test_bench_a = [ii['Answer'] for ii in test_bench]
train_bench_q = [ii['Question Text'] for ii in train_bench]
train_bench_a = [ii['Answer'] for ii in train_bench]

lp = SimilarToThis() # Lucene predictor
right = 0
total = len(test_bench_q)
print "Number of benchmark: ", total
for idx, ii in enumerate(test_bench_q):
    prediction = lp.getTopNSimilarToThis(ii)[0][0]
    print test_bench_a[idx] == prediction, test_bench_a[idx], prediction
    if prediction == test_bench_a[idx]:
        right += 1
print("Accuracy on dev: %f" % (float(right) / float(total)))
