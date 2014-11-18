from collections import defaultdict
from csv import DictReader, DictWriter

import operator
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import TreebankWordTokenizer

def form_dict(vals):
    d = defaultdict(float)
    for jj in vals.split(", "):
        key, val = jj.split(":")
        d[key.strip()] = float(val)
    return d


if __name__ == "__main__":
    d = DictReader(open("train.csv"))
    c = 0
    totaloverlap = 0.0
    nooverlap = 0
    amongtop = 0
    matchedtop = 0
    ansmatchtop = 0
    overlap = 0
    for q in d:
        c += 1
        answer = q['Answer']
        qd = form_dict(q['QANTA Scores'])
        wd = form_dict(q['IR_Wiki Scores'])
        if answer in qd or answer in wd:
            overlap += 1
        count = 0.0
        for v in qd:
            if v in wd:
                count += 1.0
        totaloverlap += (count/20.0)
        if count < 1.0:
            nooverlap += 1
        sorted_qd = sorted(qd.items(), key=operator.itemgetter(1), reverse=True)
        sorted_wd = sorted(wd.items(), key=operator.itemgetter(1), reverse=True)
        part_qd = sorted_qd[:5]
        part_wd = sorted_wd[:5]
        if sorted_qd[0][0] == sorted_wd[0][0]:
            matchedtop += 1
            if answer == sorted_qd[0][0]:
                ansmatchtop += 1
        for i in xrange(5):
            if answer in part_qd[i] or answer in part_wd[i]:
                amongtop += 1
                break
            
        """
        for v in qd:
            print qd[v]," ",
        """
        #if c == 2:
        #    break
        #print "@@@@@@@@@@@@@@@@"
    print '%.2f' % (float(ansmatchtop/float(matchedtop)) * 100.0),"%"
    print '%.2f' % (float(matchedtop)/float(c) * 100.0),"%"
    print '%.2f' % (totaloverlap/float(c-nooverlap)* 100.0),"%"
    print '%.2f' % (float(amongtop)/float(c) * 100.0),"%"
    print '%.2F' % (float(overlap)/float(c) * 100.0),"%"
