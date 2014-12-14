#!/usr/bin/env python

INDEX_DIR = "index_knowledge.index"
MAX_RESULT = 10

import sys, os, lucene
import collections

from java.io import File, StringReader
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.queries.mlt import MoreLikeThis
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.util import Version

class SimilarToThis():

    def __init__(self):
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        print 'lucene', lucene.VERSION

        self.base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.directory = SimpleFSDirectory(
                         File(os.path.join(self.base_dir, INDEX_DIR)))
        self.reader = DirectoryReader.open(self.directory)
        self.searcher = IndexSearcher(self.reader)
        self.numDocs = self.reader.maxDoc()

        self.mlt = MoreLikeThis(self.reader)
        self.mlt.setMinTermFreq(1)
        self.mlt.setMinDocFreq(1)
        self.mlt.setAnalyzer(StandardAnalyzer(Version.LUCENE_CURRENT))

    def getTopNSimilarToThis(self, question, topN=0, field=["question"],
                             max=MAX_RESULT, path=INDEX_DIR):
        if topN == 0:
            topN = self.numDocs

        self.mlt.setFieldNames(field)
        reader = StringReader(question)
        query = self.mlt.like(reader, None)
        # print query
        similarDocs = self.searcher.search(query, max)
        estimation = []
        for i in range(len(similarDocs.scoreDocs)):
            if (similarDocs.totalHits == 0):
                print "None like this"
            else:
                doc = self.reader.document(similarDocs.scoreDocs[i].doc)
                estimation.append((doc.getField('answer').stringValue(),
                                   similarDocs.scoreDocs[i].score,
                                   doc.getField('category').stringValue(),
                                   doc.getField('position').stringValue()))
        return estimation


if __name__ == '__main__':
    x = SimilarToThis()
    print x.getTopNSimilarToThis("moderator greek")
