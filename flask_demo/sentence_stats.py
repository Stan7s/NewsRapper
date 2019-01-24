# 统计新闻句子和分句的数量
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# https://github.com/fxsjy/jieba/issues/575
resentencesp = re.compile('([\n﹒﹔﹖﹗．；。！？]["’”」』]{0,2}|：(?=["‘“「『]{1,2}|$))')
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


df = pd.read_csv('data/chinese_news.csv')
sent_list = []
subsent_list = []
maxlen = 0
for row in df.itertuples():
    # print(row)
    if not pd.isnull(row.content):
        sent_list += splitsentence(row.content)
        subsent_list += splitsentence2(row.content)
# for sent in sent_list:
#     if len(sent) > maxlen:
#         maxlen = len(sent)
#         print(sent)
sent_len = [len(sent) for sent in sent_list]
sent_len = sorted(sent_len)
sent_len = sent_len[:-40]
subsent_len = [len(sent) for sent in subsent_list]

bins = np.arange(0, 150, 5)
# plt.hist(sent_len, bins=40, density=0, facecolor="blue", edgecolor="black", alpha=0.7)
plt.hist(sent_len, bins, alpha=0.5, label='sentences')
plt.hist(subsent_len, bins, alpha=0.5, label='sub sentences')
plt.legend(loc='upper right')
# 显示横轴标签
plt.xlabel("length")
# 显示纵轴标签
plt.ylabel("count")
# 显示图标题
plt.title("Chinese News Sentences' Length")
plt.show()
