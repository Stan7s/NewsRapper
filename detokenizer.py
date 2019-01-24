# 对一个文档中的句子进行detokenize

import argparse
import jieba
import pypinyin
import numpy as np
import matplotlib.pyplot as plt
import thulac
from utils import *

def merge(lines):
    '''
    处理一整篇文章
    :param article: 文章
    :return:
    '''
    new_lines = []
    for line in lines:
        words = line.split()
        s = ''
        for word in words:
            if word == '<unk>':
                continue
            elif word == '<num>':
                word = str(np.random.randint(10000))
            elif word == '<lbreak>':
                if len(s) > 0:
                    new_lines.append(s)
                s = ''
            else:
                s += word
        if len(s) > 0:
            new_lines.append(s)
    return new_lines


parser = argparse.ArgumentParser(description='Detokenizer')
parser.add_argument('--input', type=str, default='zh.test.0.tsf', help='input file name')
parser.add_argument('--output', type=str, default='detokenized.txt', help='output file name')
args = parser.parse_args()
with open(args.input, encoding="utf8") as f:
    lines = f.read().splitlines()
lines = merge(lines)
print('\n'.join(lines))
with open(args.output, encoding="utf8", mode='w') as f:
    f.write('\n'.join(lines))
