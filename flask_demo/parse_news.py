# 把新闻数据转成训练数据

import argparse
import jieba
import thulac
import pandas as pd
import numpy as np

from utils import *

def main(args):
    news_list = []
    if args.format == 'custom':
        with open(args.input, encoding='utf8') as f:
            news_list = f.read().split('<news>')
    if args.format == 'csv':
        news_list = read_from_csv(args.input, 200)
    with open(args.output, encoding='utf8', mode='w') as f:
        n = len(news_list)
        # 随机选100篇好了。。
        # 为了稳定性不随机选……
        cnt = 0
        thu1 = thulac.thulac(seg_only=True)
        for i in range(n):
            if cnt > args.threshold:
                break
            news = news_list[i]
            if i % 100 == 0:
                print("%d/%d" % (cnt, args.threshold))
            if len(news) > 0:
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
                            f.write(' '.join(line) + '\n')
                            cnt += 1
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


parser = argparse.ArgumentParser(description='Process a document')
parser.add_argument('--input', type=str, default='data/long_news.txt', help='input news file name')
parser.add_argument('--output', type=str, default='output/seg_news.txt', help='output file name')
parser.add_argument('--format', type=str, default='csv')
parser.add_argument('--segment', type=int, default=1)
parser.add_argument('--maxlen', type=int, default=15)
parser.add_argument('--threshold', type=int, default=200000)
args = parser.parse_args()
main(args)