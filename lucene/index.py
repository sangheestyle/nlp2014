#!/usr/bin/env python

INDEX_DIR = "index_knowledge.index"

import sys, os, lucene, threading, time, json
from datetime import datetime

from corpus import Corpus

from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version


class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexDocs(object):
    """Usage: python index_docs <train_path>"""

    def __init__(self, train_set, storeDir, analyzer):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(File(storeDir))
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.index_docs(train_set, writer)
        ticker = Ticker()
        print 'commit index',
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print 'done'

    def index_docs(self, train_set, writer):

        t1 = FieldType()
        t1.setIndexed(True)
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS)

        t2 = FieldType()
        t2.setIndexed(True)
        t2.setStored(True)
        t2.setTokenized(True)
        t2.setStoreTermVectorOffsets(True)
        t2.setStoreTermVectorPayloads(True)
        t2.setStoreTermVectorPositions(True)
        t2.setStoreTermVectors(True)
        t2.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        for ii in train_set:
            doc = Document()
            doc.add(Field("answer", ii['Answer'], t1))
            doc.add(Field("qid", ii['Question ID'], t1))
            doc.add(Field("category", ii['category'], t1))
            doc.add(Field("position", ii['Sentence Position'], t1))
            doc.add(Field("question", ii['Question Text'], t2))
            writer.addDocument(doc)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print IndexDocs.__doc__
        sys.exit(1)
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    start = datetime.now()
    try:
        train_path = sys.argv[1]
        train_set = Corpus()
        train_set.read(train_path)
        train_bench, test_bench = train_set.train_test_split()
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        IndexDocs(train_bench, os.path.join(base_dir, INDEX_DIR),
                   StandardAnalyzer(Version.LUCENE_CURRENT))
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
        raise e
