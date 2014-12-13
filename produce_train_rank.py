from collections import defaultdict
from csv import DictReader, DictWriter

import operator
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import TreebankWordTokenizer

kTOKENIZER = TreebankWordTokenizer()
TOPGUESSES = 40

def morphy_stem(word):
    """
        Simple stemmer
        """
    stem = wn.morphy(word)
    if stem:
        return stem.lower()
    else:
        return word.lower()

def form_dict(vals):
    d = defaultdict(float)
    for jj in vals.split(", "):
        key, val = jj.split(":")
        d[key.strip()] = float(val)
    return d


def compose_top_scores(qt_dict, ir_dict, n):
    """
        DISCARDED !!!
        Given two sets of guesses, this will return a dictionaty containing
        the n top guesses of the two models
    """
    h = n - (n/2)
    top_guesses = {}
    for i in xrange(h):
        top_guesses[qt_dict[i][0]] = float(qt_dict[i][1])
    i = 0
    c = 0
    for i in xrange(len(ir_dict)):
        if ir_dict[i][0] not in top_guesses:
            top_guesses[ir_dict[i][0]] = float(ir_dict[i][1])/10.0
        if len(top_guesses) == TOPGUESSES:
            break
    s = "."
    while len(top_guesses) < TOPGUESSES:
        s += "."
        top_guesses[s] = -1
    """
    while (i+h) < n:
    
        while True:
            if c < len(ir_dict) or ir_dict[c][0] not in top_guesses:
                break
            c += 1
        
        top_guesses[ir_dict[c][0]] = ir_dict[c][1]
        i += 1
    """
    return top_guesses

def prepare_new_trainingset(train_file):
    train_dict = DictReader(open(train_file, 'r'))
    columns = ['Question ID','Question Text','QANTA Scores','Answer','Sentence Position','IR_Wiki Scores','category','Answer Rank']
    new_train = DictWriter(open("new_train_"+str(TOPGUESSES)+".csv",'w'),columns)
    new_train.writeheader()
    t = 0
    c = 0
    for r in train_dict:
        qd = form_dict(r['QANTA Scores'])
        wd = form_dict(r['IR_Wiki Scores'])
        sorted_qd = sorted(qd.items(), key=operator.itemgetter(1), reverse=True)
        sorted_wd = sorted(wd.items(), key=operator.itemgetter(1), reverse=True)
        dict = compose_top_scores(sorted_qd, sorted_qd, TOPGUESSES)
        #dict = qd
        #sorted_scores = sorted(dict.items(), key=operator.itemgetter(1), reverse=True)
        ans = r['Answer']
        # Unknown answers (i.e., not among the top TOPGUESSES) are assigned -1
        rank = -1
        for i in xrange(TOPGUESSES):
            if i < 20:
                if sorted_qd[i][0] == ans:
                    rank = i
                    break
            else:
                if sorted_wd[i-TOPGUESSES][0] == ans:
                    rank = i
                    break
        if rank == -1:
            c += 1
        new_train.writerow({'Question ID':r['Question ID'], 'Question Text':r['Question Text'], 'QANTA Scores':r['QANTA Scores'], 'Answer':ans, 'Sentence Position':r['Sentence Position'], 'IR_Wiki Scores':r['IR_Wiki Scores'],'category':r['category'], 'Answer Rank':rank})
        t += 1
    print c, t



if __name__ == "__main__":


    prepare_new_trainingset("train.csv")

    """
    ls = []
    i = 0
    f = {}
    for t in train:
        if i > 0:
            break
    
        ls.append(t)
        f = t
        i += 1
    
    list = ls[:5]
    qd = form_dict(f['QANTA Scores'])
    wd = form_dict(f['IR_Wiki Scores'])
    sorted_qd = sorted(qd.items(), key=operator.itemgetter(1), reverse=True)
    sorted_wd = sorted(wd.items(), key=operator.itemgetter(1), reverse=True)
    dict = compose_top_scores(sorted_qd, sorted_qd, 5)
    print sorted(dict.items(), key=operator.itemgetter(1), reverse=True)
    """