from collections import defaultdict
from csv import DictReader, DictWriter

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
                if q1['Answer'] != q2 ['Answer']:
                    matches += 1.0
                    dw.writerow({'Question ID':q1['Question ID'], 'Sentence Position': q1['Sentence Position'], 'Answer':q1['Answer'], 'QANTA Scores':q1['QANTA Scores'],'IR_Wiki Scores':q1['IR_Wiki Scores'],'Question Text':q1['Question Text']})
                    qdict = form_dict(q1['QANTA Scores'])
                    wdict = form_dict(q1['IR_Wiki Scores'])
                    if q1['Answer'] not in qdict and q1['Answer'] not in wdict:
                        outofset += 1.0
                        print q1['Question ID'],"\t",q1['Sentence Position']
        c += 1.0
    print matches/c
    print outofset," questions out of the set!",c
    print outofset/c," of the questions are out of the set!"
    

def form_dict(vals):
    d = defaultdict(float)
    for jj in vals.split(", "):
        key, val = jj.split(":")
        d[key.strip()] = float(val)
    return d

if __name__ == "__main__":


    validate("train.csv","results.csv")
    """
    t = {}
    d = DictReader(open("train.csv"))
    writing_file = open("results.csv",'w')
    fieldnames = ['Question ID','Sentence Position','Answer','QANTA Scores','Question Text']
    dw = DictWriter(writing_file, delimiter=',', fieldnames=fieldnames)
    dw.writerow(dict((fn,fn) for fn in fieldnames))
    for q in d:
        values = form_dict(q['QANTA Scores'])
        h = 0
        answer = ""
        for v in values:
            if values[v] > h:
                h = values[v]
                answer = v
        dw.writerow({'Question ID':q['Question ID'],'Sentence Position':q['Sentence Position'], 'Answer':answer, 'QANTA Scores':q['QANTA Scores'],'Question Text':q['Question Text']})
        #print answer, h
    #validate("example.csv", "results.csv")
    """
