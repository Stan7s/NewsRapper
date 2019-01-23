# 把新闻数据转成训练数据

import argparse
import jieba
import re
import pandas as pd
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

resentencesp2 = re.compile('[ 　,:·，﹒﹔﹖﹗．；。！？"’”："‘“—]')
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


def main(args):
    with open(args.input, encoding='utf8') as f:
        news_list = f.read().split('<news>')
    with open(args.output, encoding='utf8', mode='w') as f:
        sent_list = []
        n = len(news_list)
        chosen = np.random.choice(n, 100)
        # 随机选100篇好了。。
        for i in range(len(chosen)):
            news = news_list[chosen[i]]
            if i % 10 == 0:
                print("%d/%d" % (i, len(chosen)))
            if len(news) > 0:
                sent_list += splitsentence2(news)
                parsed_list = []
                for sent in sent_list:
                    sent = sent.strip()
                    if len(sent) == 0:
                        continue
                    seg_list = jieba.lcut(sent)
                    seg_list2 = []
                    for word in seg_list:
                        if word == '\n' or word == '《' or word == '》':
                            continue
                        if is_number(word):
                            word = '<num>'
                        if word[-1] == '%' and is_number(word[:-1]):
                            seg_list2.append('百分之')
                            word = '<num>'
                        if word == '+':
                            word = '加'
                        if word in '、《》（）()':  # 删除标点
                            continue
                        if is_alpha(word):  # temp fix
                            continue
                        seg_list2.append(word)
                    parsed_list.append(seg_list2)

                n = len(parsed_list)
                l = -1
                line = []
                for i in range(n + 1):
                    if i == n or l + 1 + len(parsed_list[i]) > 15:
                        if l <= 0:
                            continue
                        if len(line) <= 15:
                            f.write(' '.join(line) + '\n')
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
parser.add_argument('--output', type=str, default='output/parsed_news.txt', help='output file name')
args = parser.parse_args()
main(args)