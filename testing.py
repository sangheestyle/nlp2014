from collections import defaultdict
from csv import DictReader, DictWriter

import operator
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import TreebankWordTokenizer

def validate(f1,f2):
    df1 = DictReader(open(f1))
    df2 = DictReader(open(f2))
    writing_file = open("misses.csv",'w')
    fieldnames = ['Question ID','Sentence Position','Answer','QANTA Scores','IR_Wiki Scores','Question Text']
    dw = DictWriter(writing_file, delimiter=',', fieldnames=fieldnames)
    dw.writerow(dict((fn,fn) for fn in fieldnames))
    matches = 0.0
    misses = 0.0
    d1 = []
    d2 = []
    c = 0.0
    outofset = 0.0
    for q in df1:
        d1.append(q)
    for q in df2:
        d2.append(q)
    for q1 in d1:
        for q2 in d2:
            if q1['Question ID'] == q2['Question ID'] and q1['Sentence Position'] == q2['Sentence Position']:
                if q1['Answer'] == q2 ['Answer']:
                    matches += 1.0
        c += 1.0
    print "Total number of questions =",int(c)
    print '%.2f' %(matches/c * 100.0),"% of correct answers are the top QANTA answer."
    #print outofset," incorrect selections are out of the set!"
    #print '%.2f' % (outofset/c * 100.0),"% of the incorrect selections are out of the set!"
    

def form_dict(vals):
    d = defaultdict(float)
    for jj in vals.split(", "):
        key, val = jj.split(":")
        d[key.strip()] = float(val)
    return d

if __name__ == "__main__":


    #validate("train.csv","results.csv")
    
    t = {}
    d = DictReader(open("test.csv"))
    writing_file = open("results.csv",'w')
    fieldnames = ['Question ID','Sentence Position','Answer']
    dw = DictWriter(writing_file, delimiter=',', fieldnames=fieldnames)
    dw.writerow(dict((fn,fn) for fn in fieldnames))
    answer = ""
    for q in d:
        values = form_dict(q['QANTA Scores'])
        qd = form_dict(q['QANTA Scores'])
        wd = form_dict(q['IR_Wiki Scores'])
        sorted_qd = sorted(qd.items(), key=operator.itemgetter(1), reverse=True)
        sorted_wd = sorted(wd.items(), key=operator.itemgetter(1), reverse=True)
        overlap_flag = 0
        
        for a in qd:
            if a in wd:
                overlap_flag = 1
                break
        if overlap_flag != 0:
            if sorted_qd[0][0] == sorted_wd[0][0]:
                answer = sorted_qd[0][0]
                continue
            else:
                count = 1
                for a1 in sorted_qd:
                    for a2 in sorted_wd:
                        if a1[0] == a2[0]:
                            answer = a1[0]
        else:
            answer = sorted_qd[0][0]
        dw.writerow({'Question ID':q['Question ID'],'Sentence Position':q['Sentence Position'], 'Answer':answer})
        #print answer, h
    #validate("example.csv", "results.csv")
    
