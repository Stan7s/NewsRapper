# 对一个文档中的句子进行处理

import argparse
import re
import jieba
import pypinyin
import matplotlib.pyplot as plt

resentencesp = re.compile('[,.:，﹒﹔﹖﹗．；。！？"’”："‘“—]')


def split_sentence(sentence):
    '''
    将一段话切割成分句
    :param sentence: 文段
    :return: 切割结果
    '''
    s = sentence
    slist = []
    # print(s)
    for i in resentencesp.split(s):
        if resentencesp.match(i) and slist:
            slist[-1] += i
        elif i:
            slist.append(i)
    return slist


# http://www.runoob.com/python3/python3-check-is-number.html
def is_number(s):
    '''
    判断字符串是否表示数字
    :param s:
    :return:
    '''
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


# https://leowood.github.io/2018/05/19/Python3%E5%88%A4%E6%96%AD%E5%AD%97%E7%AC%A6%E4%B8%AD%E8%8B%B1%E6%96%87%E6%95%B0%E5%AD%97%E7%AC%A6%E5%8F%B7/
def is_alphabet(char):
    '''
    判断字符是否为英文字母
    :param char:
    :return:
    '''
    if (char >= '\u0041' and char <= '\u005a') or (char >= '\u0061' and char <= '\u007a'):
        return True
    else:
        return False


def is_alpha(s):
    '''
    判断字符串是否只包含英文字母
    :param s:
    :return:
    '''
    for ch in s:
        if not is_alphabet(ch):
            return False
    return True


class Zh_Sent(object):
    def __init__(self, str, seg_list, pinyin_list, yunmu_list, tune_list):
        self.str = str
        self.seg_list = seg_list
        self.pinyin_list = pinyin_list
        self.yunmu_list = yunmu_list
        self.tune_list = tune_list

    def get_last_yunmu(self):
        return self.yunmu_list[-1][-1]

    def get_last_pinyin(self):
        return self.pinyin_list[-1][-1]

    def get_last_tone(self):
        return self.tune_list[-1][-1]


def compare_sentences(sentences):
    n = len(sentences)
    tail_similarities = []  # 最后一个字押韵的程度
    total_similarities = []  # 整体相似度
    for i in range(n):
        tail_similarities.append([])
        total_similarities.append([])
        for j in range(n):
            # 计算这两个句子的相似度
            # 最后一个字？
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

    return tail_similarities, total_similarities


def split_article(article):
    slist = split_sentence(article)
    print('句子（分句）总数：', len(slist))

    sentences = []
    for s in slist:
        s = s.strip()
        if len(s) == 0:  # patch for empty
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
                word = '零'  # temp fix
            if word[-1] == '%' and is_number(word[:-1]):
                word = '百分之五十'  # temp fix
            if word == '+':
                word = '加'
            if word in '、《》（）()':  # 删除标点
                continue
            if is_alpha(word):  # temp fix
                # print('判断为英文：', word)
                word = '英文'
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
        # print(str(seg_list2))
        # print(str(pinyin_list))
        # print(str(yunmu_list))
        # print(str(tone_list))
        sentences.append(Zh_Sent(s, seg_list2, pinyin_list, yunmu_list, tone_list))

    # 计算句子的相似度并打印
    tail_similarities, total_similarities = compare_sentences(sentences)
    for i in range(len(sentences)):
        print("sentence %d: %s" % (i, '/'.join(sentences[i].seg_list)))

    # 可视化
    img = plt.imshow(total_similarities, interpolation='nearest', cmap='gray', origin="lower")
    # make a color bar
    plt.colorbar(img, cmap='gray')
    plt.show()

    # for i in range(len(sentences)):
    #     print(str(total_similarities[i]))
        # for j in range(i+1, len(sentences)):
        #     print('(%d, %d) back similarity: %f' % (i, j, tail_similarities[i][j]))
        #     print('(%d, %d) total similarity: %f' % (i, j, total_similarities[i][j]))


parser = argparse.ArgumentParser(description='Process a document')
parser.add_argument('--filename', type=str, help='Chinese utf8 file name')
args = parser.parse_args()
with open(args.filename, encoding="utf8") as f:
    article = f.read()
    # print(article)
    split_article(article)
