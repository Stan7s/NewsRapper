# 统计新闻句子和分句的数量
import argparse
import thulac
import jieba
import matplotlib.pyplot as plt
import numpy as np
from utils import *

def calc():
    # 应该计算词数而不是字数
    sent_length_list = []
    subsent_length_list = []
    article_length_list = []
    thu1 = thulac.thulac(seg_only=True)
    news_list = read_from_csv()
    n = len(news_list)
    for i in range(n):
        if i % 200 == 0:
            print("parsed %d/%d" % (i, n))
        this_sent_list = splitsentence(news_list[i])
        this_subsent_list = []
        article_cnt = 0
        for sent in this_sent_list:
            # seg_list = thu1.cut(sent)
            seg_list = jieba.lcut(sent)
            sent_length_list.append(len(seg_list))
            article_cnt += len(seg_list)
            this_subsent_list += splitsentence2(sent)
        article_length_list.append(article_cnt)
        for subsent in this_subsent_list:
            # seg_list = thu1.cut(subsent)
            seg_list = jieba.lcut(subsent)
            subsent_length_list.append(len(seg_list))
    sent_length_list = np.array(sent_length_list)
    subsent_length_list = np.array(subsent_length_list)
    article_length_list = np.array(article_length_list)
    np.savez('data/news_stats.npz', sent_length_list=sent_length_list, subsent_length_list=subsent_length_list,
             article_length_list=article_length_list)
    return sent_length_list, subsent_length_list, article_length_list


parser = argparse.ArgumentParser(description='Process a document')
parser.add_argument('--load', type=int, default=0)
args = parser.parse_args()
if args.load == 0:
    sent_length_list, subsent_length_list, article_length_list = calc()
else:
    files = np.load('data/news_stats.npz')
    sent_length_list = files['sent_length_list']
    subsent_length_list = files['subsent_length_list']
    article_length_list = files['article_length_list']


plt.figure(1)
bins = np.arange(0, 150, 5)
# plt.hist(sent_len, bins=40, density=0, facecolor="blue", edgecolor="black", alpha=0.7)
plt.hist(sent_length_list, bins, alpha=0.5, label='sentence')
plt.hist(subsent_length_list, bins, alpha=0.5, label='simple sentence')
plt.legend(loc='upper right')
# 显示横轴标签
plt.xlabel("length")
# 显示纵轴标签
plt.ylabel("count")
# 显示图标题
plt.title("Chinese News Sentences Length (by words)")
plt.show()

plt.figure(2)
bins = np.arange(0, 150, 5)
plt.hist(article_length_list, bins, facecolor="blue", edgecolor="black", alpha=0.7)
plt.legend(loc='upper right')
# 显示横轴标签
plt.xlabel("length")
# 显示纵轴标签
plt.ylabel("count")
# 显示图标题
plt.title("Chinese News Article Length")
plt.show()