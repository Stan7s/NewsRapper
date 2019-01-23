#!/user/bin/python
# coding:utf-8

import nltk
import numpy
import jieba
import codecs
import os

class SummaryTxt:
    def __init__(self,stopwordspath):
        # 单词数量
        self.N = 100
        # 单词间的距离
        self.CLUSTER_THRESHOLD = 5
        # 返回的top n句子
        self.TOP_SENTENCES = 5
        self.stopwrods = {}
        #加载停用词
        if os.path.exists(stopwordspath):
            stoplist = [line.strip() for line in codecs.open(stopwordspath, 'r', encoding='utf8').readlines()]
            self.stopwrods = {}.fromkeys(stoplist)


    def _split_sentences(self,texts):
        '''
        把texts拆分成单个句子，保存在列表里面，以（.!?。！？）这些标点作为拆分的意见，
        :param texts: 文本信息
        :return:
        '''
        splitstr = '.!?。！？'.decode('utf8')
        start = 0
        index = 0  # 每个字符的位置
        sentences = []
        for text in texts:
            if text in splitstr:  # 检查标点符号下一个字符是否还是标点
                sentences.append(texts[start:index + 1])  # 当前标点符号位置
                start = index + 1  # start标记到下一句的开头
            index += 1
        if start < len(texts):
            sentences.append(texts[start:])  # 这是为了处理文本末尾没有标

        return sentences

    def _score_sentences(self,sentences, topn_words):
        '''
        利用前N个关键字给句子打分
        :param sentences: 句子列表
        :param topn_words: 关键字列表
        :return:
        '''
        scores = []
        sentence_idx = -1
        for s in [list(jieba.cut(s)) for s in sentences]:
            sentence_idx += 1
            word_idx = []
            for w in topn_words:
                try:
                    word_idx.append(s.index(w))  # 关键词出现在该句子中的索引位置
                except ValueError:  # w不在句子中
                    pass
            word_idx.sort()
            if len(word_idx) == 0:
                continue
            # 对于两个连续的单词，利用单词位置索引，通过距离阀值计算族
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
            # 对每个族打分，每个族类的最大分数是对句子的打分
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
        # 将文章分成句子
        sentences = self._split_sentences(text)

        # 生成分词
        words = [w for sentence in sentences for w in jieba.cut(sentence) if w not in self.stopwrods if
                 len(w) > 1 and w != '\t']
        # words = []
        # for sentence in sentences:
        #     for w in jieba.cut(sentence):
        #         if w not in stopwords and len(w) > 1 and w != '\t':
        #             words.append(w)

        # 统计词频
        wordfre = nltk.FreqDist(words)

        # 获取词频最高的前N个词
        topn_words = [w[0] for w in sorted(wordfre.items(), key=lambda d: d[1], reverse=True)][:self.N]

        # 根据最高的n个关键词，给句子打分
        scored_sentences = self._score_sentences(sentences, topn_words)

        # 利用均值和标准差过滤非重要句子
        avg = numpy.mean([s[1] for s in scored_sentences])  # 均值
        std = numpy.std([s[1] for s in scored_sentences])  # 标准差
        summarySentences = []
        for (sent_idx, score) in scored_sentences:
            if score > (avg + 0.5 * std):
                summarySentences.append(sentences[sent_idx])
                print(sentences[sent_idx])
        return summarySentences

    def summaryTopNtxt(self,text):
        # 将文章分成句子
        sentences = self._split_sentences(text)

        # 根据句子列表生成分词列表
        words = [w for sentence in sentences for w in jieba.cut(sentence) if w not in self.stopwrods if
                 len(w) > 1 and w != '\t']
        # words = []
        # for sentence in sentences:
        #     for w in jieba.cut(sentence):
        #         if w not in stopwords and len(w) > 1 and w != '\t':
        #             words.append(w)

        # 统计词频
        wordfre = nltk.FreqDist(words)

        # 获取词频最高的前N个词
        topn_words = [w[0] for w in sorted(wordfre.items(), key=lambda d: d[1], reverse=True)][:self.N]

        # 根据最高的n个关键词，给句子打分
        scored_sentences = self._score_sentences(sentences, topn_words)

        top_n_scored = sorted(scored_sentences, key=lambda s: s[1])[-self.TOP_SENTENCES:]
        top_n_scored = sorted(top_n_scored, key=lambda s: s[0])
        summarySentences = []
        for (idx, score) in top_n_scored:
            print(sentences[idx])
            summarySentences.append(sentences[idx])

        return sentences


if __name__=='__main__':
    obj =SummaryTxt('D:\work\Solr\solr-python\CNstopwords.txt')

    txt=u'习总书记指出，要解决好“扶持谁”的问题，确保把真正的贫困人口弄清楚，把贫困人口、贫困程度、致贫原因等搞清楚，以便做到因户施策、因人施策。当下，湖北巴东县正在进行贫困户建档立卡的“回头看”工作。《治国理政新实践》专栏继续播出《脱贫军令状》系列报道，看看湖北巴东的县乡干部如何通过“院子会”等形式确保扶真贫、真扶贫。' \
        u'陈行甲是巴东县委书记，在这个国家级贫困县，全县33万农民，14.7万是贫困人口。真正把贫困人口、贫困程度、致贫原因等搞清楚，是这一次“回头看”的主要内容。这个任务，县里交给了包村干部，陈行甲想看看，干部“回头看”，用没用心，摸没摸清。' \
        u'电话那头，是镇干部李俊，他和贫困户黄克卓结对。这次暗访，陈行甲发现，李俊到村里点个卯、照张相就走了，“回头看”成了走形式。' \
        u'在县大会上，李俊被点名批评，在全镇干部大会上，他也做了检讨。从去年年底开始，县里派出六个督办组，进村入户探访扶贫工作，发现干部敷衍塞责，就公开通报，甚至免职。' \
        u'这次“回头看”，除了让干部去贫困户走访，再摸家底，县里还要求每个村都开“院子会”，县乡的包村干部必须参加。各村各户，谁穷谁不穷，乡里乡亲最清楚，干部要通过院子会，看看以前建档立卡的贫困户中，有没有不公平的。' \
        u'在茶店子镇教场坝村的院子会上，县乡干部现场监督，村民们当面锣、对面鼓，讨论起了贫困户的名单。一位村民对自己在这一轮识别中，要被从名单上拿下来，很是不满。' \
        u'原来这位村民的儿子刚刚考上公务员，公务员家庭不算贫困户，是巴东县的硬性规定。' \
        u'村民提到的税典尧，之前一直在外地打工有收入，不算贫困户。一年多前出了事故，一直在外地治疗，如今花光了积蓄，属于典型的因病致贫。院子会上，干部们记下了这些意见，准备重新入户调查。' \
        u'把贫困的情况摸的更细更清楚，发生了变化就及时动态调整，正是巴东开展“回头看”的目的。院子会一开，村民们对政府的扶贫情况，心里更明白了。' \
        u'用开院子会的方式进行评议，也是县里根据实际情况决定的。巴东山多，当地人说“看山跑死马”，如果开全村大会，很多人要翻山越岭，很难到齐。“院子会”以院子或连片农户为单元，每户选一个人参加。左邻右舍挨得近，这轮“回头看”，用小会评议贫困户，方便可行。' \
        u'根据湖北省扶贫工作的统一要求，全省建档立卡回头看的工作要在本月底前完成。目前，巴东所有包村干部已经全部进驻村组，召开了5000多场次的院子会，收集了近六万条村民意见和建议。不久后，巴东县还将建立数据库，把干部们扶贫的每一步举措，都进行动态管理，随时掌握。' \
        u'派出督办组，让乡镇干部“沉下去”；召开“院子会”，让真实情况“浮上来”。巴东县确保扶真贫、真扶贫的做法，实质上就是在改进干部作风上下功夫，在创新工作方法上做文章。要让扶贫扶到点子上，要让脱贫效果能牢固，必须打造一支肯干会干的扶贫干部队伍，这就要求基层党员干部对脱贫攻坚必须认识到位、作风扎实、方法得当。这是精准扶贫的内在逻辑，也是精准脱贫的必然要求。'
    # txt ='The information disclosed by the Film Funds Office of the State Administration of Press, Publication, Radio, Film and Television shows that, the total box office in China amounted to nearly 3 billion yuan during the first six days of the lunar year (February 8 - 13), an increase of 67% compared to the 1.797 billion yuan in the Chinese Spring Festival period in 2015, becoming the "Best Chinese Spring Festival Period in History".' \
    #      'During the Chinese Spring Festival period, "The Mermaid" contributed to a box office of 1.46 billion yuan. "The Man From Macau III" reached a box office of 680 million yuan. "The Journey to the West: The Monkey King 2" had a box office of 650 million yuan. "Kung Fu Panda 3" also had a box office of exceeding 130 million. These four blockbusters together contributed more than 95% of the total box office during the Chinese Spring Festival period.' \
    #      'There were many factors contributing to the popularity during the Chinese Spring Festival period. Apparently, the overall popular film market with good box office was driven by the emergence of a few blockbusters. In fact, apart from the appeal of the films, other factors like film ticket subsidy of online seat-selection companies, cinema channel sinking and the film-viewing heat in the middle and small cities driven by the home-returning wave were all main factors contributing to this blowout. A management of Shanghai Film Group told the 21st Century Business Herald.'
    print(txt)
    print("--")
    obj.summaryScoredtxt(txt)

    print("----")
    obj.summaryTopNtxt(txt)