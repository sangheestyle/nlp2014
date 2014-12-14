from nltk.corpus.reader.conll import ConllCorpusReader


class StanfordCorpusReader(object):
    """
    Read text parsed by Stanford Parser
    """

    def __init__(self, root):
        self._root = root

    def get_text(self, keyword):
        """
        Return a complete text of the keyword
        """
        items = ['ignore', 'words', 'ignore', 'ignore', 'ignore']
        corpus = self._get_conll_corpus(keyword, items)
        text = []
        for ii in corpus.sents():
            text.append(" ".join(ii))
        return "\n".join(text)

    def _get_conll_corpus(self, keyword, items):
        keyword_path = keyword[0] + "/" + keyword
        corpus = ConllCorpusReader(self._root, keyword_path,
                                   items, encoding='utf=8')
        return corpus


if __name__ == "__main__":
    sc = StanfordCorpusReader('wikipedia')
    print sc.get_text("aztec_mythology")
