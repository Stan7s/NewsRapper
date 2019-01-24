# 对一个文档中的句子进行处理

import argparse
import jieba
import pypinyin
import numpy as np
import matplotlib.pyplot as plt
from utils import *


class Zh_Sent(object):
    def __init__(self, str, seg_list, pinyin_list, yunmu_list, tone_list):
        self.str = str
        self.seg_list = seg_list
        self.pinyin_list = pinyin_list
        self.yunmu_list = yunmu_list
        self.tone_list = tone_list
        self.length = 0
        for seg in self.seg_list:
            self.length += len(seg)

    def get_last_yunmu(self):
        return self.yunmu_list[-1][-1]

    def get_last_pinyin(self):
        return self.pinyin_list[-1][-1]

    def get_last_tone(self):
        return self.tone_list[-1][-1]


# https://stackoverflow.com/questions/2460177/edit-distance-in-python
def calc_edit_distance(s1, s2):
    '''
    计算s1和s2之间的编辑距离
    :param s1:
    :param s2:
    :return:
    '''
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def compare_sentences(sentences):
    '''
    计算两句话的相似度
    :param sentences:
    :return:
    '''
    n = len(sentences)
    length_similarities = [] # 长度接近程度
    tail_similarities = []  # 最后一个字押韵的程度
    total_similarities = []  # 节奏相似度
    edit_distance = []
    for i in range(n):
        length_similarities.append([])
        tail_similarities.append([])
        total_similarities.append([])
        edit_distance.append([])
        for j in range(n):
            # 计算这两个句子的相似度
            # 编辑距离
            edit_distance[-1].append(calc_edit_distance(sentences[i].str, sentences[j].str))
            # 长度的相似度？
            l1 = sentences[i].length
            l2 = sentences[j].length
            m = min(l1, l2)
            length_similarities[-1].append((l1 + l2 - 2*m) / (l1 + l2))
            # 计算最后一个字的相似度？
            if sentences[i].get_last_pinyin() == sentences[j].get_last_pinyin():
                tail = 1.0
            elif sentences[i].get_last_yunmu() == sentences[j].get_last_yunmu():
                tail = 0.7
            elif sentences[i].get_last_tone() == sentences[j].get_last_tone():
                tail = 0.2
            else:
                tail = 0.0
            tail_similarities[-1].append(tail)
            # 从每个字开始的节奏的匹配？
            # 应该取最大值而不是所有值。
            total = 0
            for k in range(len(sentences[j].seg_list)):
                # sentences[i][0]开始尝试和sentences[j][k]匹配
                i1 = 0
                i2 = k
                cnt = 0
                sum1 = len(sentences[i].seg_list[i1])
                sum2 = len(sentences[j].seg_list[i2])
                while i1 < len(sentences[i].seg_list) and i2 < len(sentences[j].seg_list):
                    if sum1 < sum2:
                        i1 += 1
                        if i1 >= len(sentences[i].seg_list):
                            break
                        sum1 += len(sentences[i].seg_list[i1])
                    elif sum1 > sum2:
                        i2 += 1
                        if i2 >= len(sentences[j].seg_list):
                            break
                        sum2 += len(sentences[j].seg_list[i2])
                    else:
                        cnt += 1
                        i1 += 1
                        i2 += 1
                        if i1 >= len(sentences[i].seg_list) or i2 >= len(sentences[j].seg_list):
                            break
                        sum1 = len(sentences[i].seg_list[i1])
                        sum2 = len(sentences[j].seg_list[i2])
                total = max(cnt, total)
            total_similarities[-1].append(total * 2 / (len(sentences[i].seg_list) + len(sentences[j].seg_list)))

    return np.array(edit_distance), np.array(length_similarities), np.array(tail_similarities), np.array(total_similarities)


def find_path(graph, threshold):
    n = len(graph)
    f = np.zeros(n, dtype=np.int)
    last = np.zeros(n, dtype=np.int)
    f[0] = 1
    last[0] = -1
    maxlen = 0
    ans = -1
    for i in range(1, n):
        f[i] = 1
        for j in range(0, i):
            if f[j] + 1 > f[i] and graph[i, j] >= threshold:
                last[i] = j
                f[i] = f[j] + 1
        if f[i] > maxlen:
            maxlen = f[i]
            ans = i
    path = []
    while not ans == -1:
        path.append(ans)
        ans = last[ans]
    path.reverse()
    return path


# 把一个过长的句子分成几段
def cut_sentences(sentence, force=-1):
    if sentence.length <= 12 and force == -1:
        return [sentence]
    sent_list = []
    seg_list = []
    pinyin_list = []
    yunmu_list = []
    tone_list = []
    length = 0
    n = len(sentence.seg_list)
    # print('/'.join(sentence.seg_list))
    for i in range(n + 1):
        # print(length)
        if i == n or (force == -1 and length >= 6 or not force == -1 and length >= force):
            if force == -1 and length >= 6 or not force == -1 and length == force:
                sent_list.append(Zh_Sent(''.join(seg_list), seg_list, pinyin_list, yunmu_list, tone_list))
            seg_list = []
            pinyin_list = []
            yunmu_list = []
            tone_list = []
            length = 0
            if i == n:
                break
        length += len(sentence.seg_list[i])
        seg_list.append(sentence.seg_list[i])
        pinyin_list.append(sentence.pinyin_list[i])
        yunmu_list.append(sentence.yunmu_list[i])
        tone_list.append(sentence.tone_list)
    return sent_list


def split_article(article):
    '''
    处理一整篇文章
    :param article: 文章
    :return:
    '''
    slist = splitsentence2(article)
    print('分句总数：', len(slist))

    sentences = []
    for s in slist:
        s = s.strip()
        if len(s) == 0:  # patch for empty
            continue
        if len(s) < 5:  # 删除词数太少的句子
            continue
        seg_list = jieba.lcut(s)  # list cut
        if len(seg_list) == 0:  # patch for empty
            continue
        seg_list2 = []
        # 筛掉\n之类奇怪的东西，同时去掉标点符号
        for word in seg_list:
            if word == '\n' or word == '《' or word == '》':
                continue
            if is_number(word):
                # print(word)
                word = float2cn(word)  # queer fix
            if word[-1] == '%' and is_number(word[:-1]):
                seg_list2.append('百分之')
                word = float2cn(word[:-1])  # queer fix
            if word == '+':
                word = '加'
            if word in '、《》（）()':  # 删除标点
                continue
            if is_alpha(word):  # temp fix
                # print('判断为英文：', word)
                # word = '英文'
                pass
            seg_list2.append(word)
        if len(seg_list2) == 0:  # patch for empty
            continue
        pinyin_list = []
        yunmu_list = []
        tone_list = []
        for word in seg_list2:
            pinyin_list.append(pypinyin.lazy_pinyin(word))
            yunmu_list.append(pypinyin.lazy_pinyin(word, style=pypinyin.Style.FINALS))
            tones = pypinyin.lazy_pinyin(word, style=pypinyin.Style.TONE3)
            for i in range(len(tones)):
                if not is_alphabet(tones[i][-1]):
                    tones[i] = int(tones[i][-1])
                else:
                    tones[i] = 0
            tone_list.append(tones)
        # print('/'.join(seg_list2))
        # print(str(pinyin_list))
        # print(str(yunmu_list))
        # print(str(tone_list))
        # 把过长的句子拆开
        sent = cut_sentences(Zh_Sent(s, seg_list2, pinyin_list, yunmu_list, tone_list), force=args.force_same)
        sentences += sent

    for i in range(len(sentences)):
        print("sentence %d: %s" % (i, '/'.join(sentences[i].seg_list)))

    # 计算句子的相似度
    edit_distance, length_similarities, tail_similarities, total_similarities = compare_sentences(sentences)
    # edit distance
    too_similiar_mask = np.greater(edit_distance, 1).astype(np.float)
    # 值是随便取的
    similarities = 0.5 * length_similarities + 0.4 * tail_similarities + 0.1 * total_similarities
    similarities = np.multiply(similarities, too_similiar_mask)

    # 可视化
    if args.show == 1:
        img = plt.imshow(similarities, interpolation='nearest', cmap='gray', origin="lower")
        # make a color bar
        plt.colorbar(img, cmap='gray')
        plt.show()

    # 二分答案 + DP找总长度大于20的句子
    l = 0.0
    r = 1.0
    while r - l > 1e-6:
        m = (l + r) / 2.0
        path = find_path(similarities, m)
        if len(path) >= 20:
            l = m
        else:
            r = m
    print('最大相似度：', m)
    print(str(path))
    selected = []
    for i in path:
        selected.append(''.join(sentences[i].seg_list))
    return selected


parser = argparse.ArgumentParser(description='Process a document')
parser.add_argument('--filename', type=str, help='Chinese utf8 file name')
parser.add_argument('--force_same', type=int, default=-1, help='Force each segment to have same length')
parser.add_argument('--show', type=int, default=1, help='Show matplotlib picture')
args = parser.parse_args()
with open(args.filename, encoding="utf8") as f:
    article = f.read()
    # print(article)
    selected = split_article(article)
    print('\n'.join(selected))
