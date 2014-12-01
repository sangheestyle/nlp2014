from collections import defaultdict
from csv import DictReader, DictWriter

import operator
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import TreebankWordTokenizer

kTOKENIZER = TreebankWordTokenizer()
TOPGUESSES = 20
def morphy_stem(word):
    """
    Simple stemmer
    """
    stem = wn.morphy(word)
    if stem:
        return stem.lower()
    else:
        return word.lower()

def compose_top_scores(qt_dict, ir_dict, n):
    """
        Given two sets of guesses, this will return a dictionaty containing
        the n top guesses of the two models
    """
    h = n - (n/2)
    top_guesses = {}
    for i in xrange(h):
        top_guesses[qt_dict[i][0]] = qt_dict[i][1]
    i = 0
    c = 0
    
    while (i+h) < n:
        while True:
            if ir_dict[c][0] not in top_guesses:
                break
            c += 1
        top_guesses[ir_dict[c][0]] = ir_dict[c][1]
        i += 1

    return top_guesses

def get_answer(qt_dict, ir_dict, n, rank):
    """
        This will return the answer ranked "rank" among the top guesses generated by compose_top_scores
    """
    h = n - (n/2)
    if rank < h:
        return qt_dict[rank][0]
    else:
        return ir_dict[rank-h][0]

def form_dict(vals):
    d = defaultdict(float)
    for jj in vals.split(", "):
        key, val = jj.split(":")
        d[key.strip()] = float(val)
    return d


class FeatureExtractor:
    def __init__(self):
        """
        You may want to add code here
        """
        
        None
    
    def features(self, dict):
        d = defaultdict(int)
        """
        for ii in kTOKENIZER.tokenize(dict['Question Text']):
            d[morphy_stem(ii)] += 1
        """
        qd = form_dict(dict['QANTA Scores'])
        wd = form_dict(dict['IR_Wiki Scores'])
        
        for g in qd:
            if g in wd:
                d['Overlap'] += 1
                
        
        sorted_qd = sorted(qd.items(), key=operator.itemgetter(1), reverse=True)
        sorted_wd = sorted(wd.items(), key=operator.itemgetter(1), reverse=True)
        
        for qg in xrange(TOPGUESSES):
            if sorted_qd[qg][0] == sorted_wd[0][0]:
                d['Top Overlap'] += 20-qg
        
        d['Sentence Position'] = int(dict['Sentence Position'])
        
        return d

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--subsample', type=float, default=1.0,
                        help='subsample this amount')
    args = parser.parse_args()
    
    # Create feature extractor (you may want to modify this)
    fe = FeatureExtractor()
    
    # Read in training data
    train = DictReader(open("new_train_"+str(TOPGUESSES)+".csv", 'r'))
    
    # Split off dev section
    dev_train = []
    dev_test = []
    
    for ii in train:
        if args.subsample < 1.0 and int(ii['Question ID']) % 100 > 100 * args.subsample:
            continue

        dict = {}
        dict['Question Text'] = ii['Question Text']
        dict['QANTA Scores'] = ii['QANTA Scores']
        dict['IR_Wiki Scores'] = ii['IR_Wiki Scores']
        dict['Sentence Position'] = ii['Sentence Position']
        dict['category'] = ii['category']
        feat = fe.features(dict)
        if int(ii['Question ID']) % 5 == 0:
            dev_test.append((feat, ii['Answer Rank']))
        else:
            dev_train.append((feat, ii['Answer Rank']))

    # Train a classifier
    print("Training classifier ...")
    classifier = nltk.classify.NaiveBayesClassifier.train(dev_train)
    #classifier = nltk.classify.MaxentClassifier.train(dev_train, 'IIS', trace=3, max_iter=100)

    right = 0
    total = len(dev_test)
    for ii in dev_test:
        prediction = classifier.classify(ii[0])
        if prediction == ii[1]:
            right += 1
    print("Accuracy on dev: %f" % (float(right) / float(total)))

    # Retrain on all data
    classifier = nltk.classify.NaiveBayesClassifier.train(dev_train + dev_test)
    #classifier = nltk.classify.MaxentClassifier.train(dev_train+ dev_test, 'IIS', trace=3, max_iter=1000)
    # Read in test section
    test = {}
    for ii in DictReader(open("test.csv")):
        dict = {}
        dict['Question Text'] = ii['Question Text']
        dict['QANTA Scores'] = ii['QANTA Scores']
        dict['IR_Wiki Scores'] = ii['IR_Wiki Scores']
        dict['Sentence Position'] = ii['Sentence Position']
        dict['category'] = ii['category']
        qd = form_dict(dict['QANTA Scores'])
        wd = form_dict(dict['IR_Wiki Scores'])
        sorted_qd = sorted(qd.items(), key=operator.itemgetter(1), reverse=True)
        sorted_wd = sorted(wd.items(), key=operator.itemgetter(1), reverse=True)
        test[ii['Question ID']] = classifier.classify(fe.features(dict))
        rank = int(test[ii['Question ID']])
        #print rank
        if rank < 0:
            test[ii['Question ID']] = sorted_qd[0][0]
        else:
            test[ii['Question ID']] = get_answer(sorted_qd, sorted_qd, TOPGUESSES, rank)

    # Write predictions
    o = DictWriter(open('pred.csv', 'w'), ['Question ID', 'Answer'])
    o.writeheader()
    for ii in sorted(test):
        o.writerow({'Question ID': ii, 'Answer': test[ii]})







