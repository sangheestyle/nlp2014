from nltk.corpus.reader.conll import ConllCorpusReader


class StanfordCorpusReader(object):
    """
    Read text parsed by Stanford Parser
    """

    def __init__(self, root):
        self._root = root
        self._column_types = ['ignore', 'words', 'ignore',
                              'ignore', 'ignore']

    def get_text(self, keyword):
        """
        Return a complete text of the keyword
        """
        wiki_path = self._root + "/" + keyword[0] + "/" + keyword
        corpus = self._get_conll_corpus(wiki_path, self._column_types)
        text = []
        try:
            for ii in corpus.sents():
                text.append(" ".join(ii))
            return "\n".join(text)
        except:
            print "Not found", wiki_path
            return ""

    def _get_conll_corpus(self, wiki_path, column_types):
        corpus = ConllCorpusReader("", wiki_path, column_types)
        return corpus


if __name__ == "__main__":
    sc = StanfordCorpusReader('wikipedia')
    print sc.get_text("aztec_mythology")
