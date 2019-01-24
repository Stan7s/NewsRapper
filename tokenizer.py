# 对一个文档中的句子进行tokenize

import argparse
import jieba
import pypinyin
import numpy as np
import matplotlib.pyplot as plt
import thulac
from utils import *

def split_article(args, article):
    '''
    处理一整篇文章
    :param article: 文章
    :return:
    '''

    output_lines = []

    thu1 = thulac.thulac(seg_only=True)
    news = article
    sent_list = splitsentence2(news)
    parsed_list = []
    for sent in sent_list:
        sent = sent.strip()
        if len(sent) == 0:
            continue
        # 分词
        if args.segment == 0:
            seg_list = jieba.lcut(sent)
        else:
            seg_list = thu1.cut(sent)
            seg_list = [t[0] for t in seg_list]
        seg_list2 = []
        for word in seg_list:
            seg_list2 += parse_segged_word(word)
        # 不分词
        if args.segment == 0:
            seg_list3 = []
            for word in seg_list2:
                if word == '<num>':
                    seg_list3.append(word)
                else:
                    seg_list3 += list(word)
            seg_list2 = seg_list3
        if len(seg_list2) > 0:
            parsed_list.append(seg_list2)

    # 取maxlen长度的句子
    n = len(parsed_list)
    l = -1
    line = []
    for i in range(n + 1):
        if i == n or l + 1 + len(parsed_list[i]) > args.maxlen:
            if l <= 0:
                continue
            if len(line) <= args.maxlen:
                output_lines.append(' '.join(line))
            l = -1
            line = []
            if i == n:
                break
        if l != -1:
            line.append('<lbreak>')
            l += 1
        else:
            l = 0
        line += parsed_list[i]
        l += len(parsed_list[i])

    return output_lines


parser = argparse.ArgumentParser(description='Process an article')
parser.add_argument('--input', type=str, default='data/news_content/news_1.txt', help='input news file name')
parser.add_argument('--output', type=str, default='output/segged_news_1.txt', help='output file name')
parser.add_argument('--segment', type=int, default=1)
parser.add_argument('--maxlen', type=int, default=15)
args = parser.parse_args()
with open(args.input, encoding="utf8") as f:
    article = f.read()
seg_lines = split_article(args, article)
print('\n'.join(seg_lines))
with open(args.output, encoding="utf8", mode='w') as f:
    f.write('\n'.join(seg_lines))

