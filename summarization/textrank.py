#!/user/bin/python
# coding=utf-8

import nltk
import numpy
import jieba
import codecs
import os


class SummaryTxt:
    def __init__(self,stopwordspath):
        self.N = 100
        self.CLUSTER_THRESHOLD = 5
        self.TOP_SENTENCES = 5
        self.stopwrods = {}
        if os.path.exists(stopwordspath):
            stoplist = [line.strip() for line in codecs.open(stopwordspath, 'r', encoding='utf8').readlines()]
            self.stopwrods = {}.fromkeys(stoplist)


    def _split_sentences(self,texts):
        splitstr = '.!?。！？'.decode('utf8')
        start = 0
        index = 0
        sentences = []
        for text in texts:
            if text in splitstr:
                sentences.append(texts[start:index + 1])
                start = index + 1
            index += 1
        if start < len(texts):
            sentences.append(texts[start:])

        return sentences

    def _score_sentences(self,sentences, topn_words):
        scores = []
        sentence_idx = -1
        for s in [list(jieba.cut(s)) for s in sentences]:
            sentence_idx += 1
            word_idx = []
            for w in topn_words:
                try:
                    word_idx.append(s.index(w))
                except ValueError:  # w is not in sentence
                    pass
            word_idx.sort()
            if len(word_idx) == 0:
                continue
            clusters = []
            cluster = [word_idx[0]]
            i = 1
            while i < len(word_idx):
                if word_idx[i] - word_idx[i - 1] < self.CLUSTER_THRESHOLD:
                    cluster.append(word_idx[i])
                else:
                    clusters.append(cluster[:])
                    cluster = [word_idx[i]]
                i += 1
            clusters.append(cluster)
            max_cluster_score = 0
            for c in clusters:
                significant_words_in_cluster = len(c)
                total_words_in_cluster = c[-1] - c[0] + 1
                score = 1.0 * significant_words_in_cluster * significant_words_in_cluster / total_words_in_cluster
                if score > max_cluster_score:
                    max_cluster_score = score
            scores.append((sentence_idx, max_cluster_score))
        return scores

    def summaryScoredtxt(self,text):
        sentences = self._split_sentences(text)
        words = [w for sentence in sentences for w in jieba.cut(sentence) if w not in self.stopwrods if
                 len(w) > 1 and w != '\t']
        wordfre = nltk.FreqDist(words)
        topn_words = [w[0] for w in sorted(wordfre.items(), key=lambda d: d[1], reverse=True)][:self.N]
        scored_sentences = self._score_sentences(sentences, topn_words)
        avg = numpy.mean([s[1] for s in scored_sentences])
        std = numpy.std([s[1] for s in scored_sentences])
        summarySentences = []
        for (sent_idx, score) in scored_sentences:
            if score > (avg + 0.5 * std):
                summarySentences.append(sentences[sent_idx])
                print(sentences[sent_idx])
        return summarySentences

    def summaryTopNtxt(self,text):
        sentences = self._split_sentences(text)

        words = [w for sentence in sentences for w in jieba.cut(sentence) if w not in self.stopwrods if
                 len(w) > 1 and w != '\t']
        wordfre = nltk.FreqDist(words)
        topn_words = [w[0] for w in sorted(wordfre.items(), key=lambda d: d[1], reverse=True)][:self.N]
        scored_sentences = self._score_sentences(sentences, topn_words)

        top_n_scored = sorted(scored_sentences, key=lambda s: s[1])[-self.TOP_SENTENCES:]
        top_n_scored = sorted(top_n_scored, key=lambda s: s[0])
        summarySentences = []
        for (idx, score) in top_n_scored:
            print(sentences[idx])
            summarySentences.append(sentences[idx])
        return sentences


if __name__ == '__main__':
    obj =SummaryTxt('stopwords.txt')
    with open('news.txt', 'r') as f:
        text = f.read()
        text = text.decode('utf-8')
    print(text)
    print("----")
    obj.summaryScoredtxt(text)
    print("----")
    obj.summaryTopNtxt(text)