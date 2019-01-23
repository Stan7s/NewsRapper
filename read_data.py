import pandas as pd
import pypinyin
import jieba
import re
import random

# https://github.com/fxsjy/jieba/issues/575
resentencesp = re.compile('([﹒﹔﹖﹗．；。！？]["’”」』]{0,2}|：(?=["‘“「『]{1,2}|$))')
def splitsentence(sentence):
    s = sentence
    slist = []
    # print(s)
    for i in resentencesp.split(s):
        if resentencesp.match(i) and slist:
            slist[-1] += i
        elif i:
            slist.append(i)
    return slist

resentencesp2 = re.compile('[ ,:·，﹒﹔﹖﹗．；。！？"’”："‘“—]')
def splitsentence2(sentence):
    s = sentence
    slist = []
    # print(s)
    for i in resentencesp2.split(s):
        if resentencesp2.match(i) and slist:
            slist[-1] += i
        elif i:
            slist.append(i)
    return slist

# http://www.runoob.com/python3/python3-check-is-number.html
def is_number(s):
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
    if (char >= '\u0041' and char <= '\u005a') or (char >= '\u0061' and char <= '\u007a'):
        return True
    else:
        return False

# 判断字符串是否为全英文
def is_alpha(s):
    for ch in s:
        if not is_alphabet(ch):
            return False
    return True

class Zh_Sent(object):
    def __init__(self, str, seg_list, pinyin_list, yunmu_list):
        self.str = str
        self.seg_list = seg_list
        self.pinyin_list = pinyin_list
        self.yunmu_list = yunmu_list

    def get_last_yunmu(self):
        # print(self.yunmu_list)
        # l = self.yunmu_list[-1]
        # print(str(l))
        # print(l[-1])
        # return l[-1]
        return self.yunmu_list[-1][-1]

    def get_last_pinyin(self):
        return self.pinyin_list[-1][-1]

df = pd.read_csv('data/chinese_news.csv')
slist = []
for row in df.itertuples():
    # print(row)
    if not pd.isnull(row.content):
        slist += splitsentence2(row.content)
print('句子（分句）总数：', len(slist))
# print(str(slist))

i = 0

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
            print('判断为英文：', word)
            word = '英文'
        seg_list2.append(word)
    if len(seg_list2) == 0:  # patch for empty
        continue
    pinyin_list = []
    yunmu_list = []
    for word in seg_list2:
        pinyin_list.append(pypinyin.lazy_pinyin(word))
        yunmu_list.append(pypinyin.lazy_pinyin(word, style=pypinyin.Style.FINALS))
    # print(str(seg_list2))
    # print(str(pinyin_list))
    # print(str(yunmu_list))
    sentences.append(Zh_Sent(s, seg_list2, pinyin_list, yunmu_list))

    i += 1
    if i % 1000 == 0:
        print('已处理%d句……' % i)
    if i >= 10000:
        break

yunmu_dict = {}
pinyin_dict = {}

for i in range(len(sentences)):
    if sentences[i].get_last_yunmu() in yunmu_dict:
        yunmu_dict[sentences[i].get_last_yunmu()].append(i)
    else:
        yunmu_dict[sentences[i].get_last_yunmu()] = [i]
    if sentences[i].get_last_pinyin() in pinyin_dict:
        pinyin_dict[sentences[i].get_last_pinyin()].append(i)
    else:
        pinyin_dict[sentences[i].get_last_pinyin()] = [i]

# 检查结果
for yunmu, sents in yunmu_dict.items():
    print(yunmu + ': ' + str(len(sents)))
    for i in range(min(2, len(sents))):
        rand = random.randrange(len(sents))
        print(sentences[sents[rand]].str)