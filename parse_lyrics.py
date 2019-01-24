# 把歌词转成训练数据形式

import argparse
import jieba
import thulac
from hanziconv import HanziConv
from utils import *
import os


def main(args):
    with open(args.input, encoding='utf8') as f:
        lines = f.read().splitlines()
        if args.format == 'lines':
            lines.append('<song>')
        tot = len(lines)
    parsed_line = []
    thu1 = thulac.thulac(seg_only=True)
    with open(args.output, encoding='utf8', mode='w') as f:
        cnt = 0
        for line in lines:
            if args.format == 'lines':
                line = HanziConv.toSimplified(line)
            if cnt % 100 == 0:
                print('status: %d/%d' % (cnt, tot))
            cnt += 1
            if line == '<song>':
                if len(parsed_line) == 0:
                    continue
                n = len(parsed_line)
                # 控制每句总长度为maxlen
                for i in range(n):
                    l = len(parsed_line[i])
                    if l > args.maxlen:
                        continue
                    ctrl_list = parsed_line[i]
                    for k in range(i+1, n+1):
                        if k == n or l + len(parsed_line[k]) + 1 > args.maxlen:
                            f.write(' '.join(ctrl_list) + '\n')
                            break
                        ctrl_list.append('<lbreak>')
                        ctrl_list += parsed_line[k]
                        l += len(parsed_line[k]) + 1
                parsed_line = []
                continue
            # 用thulac或jieba进行分词
            if args.segment == 0:
                seg_list = jieba.lcut(line)
            else:
                seg_list = thu1.cut(line)
                seg_list = [t[0] for t in seg_list]
            seg_list2 = []
            for word in seg_list:
                seg_list2 += parse_segged_word(word)
            seg_list = seg_list2
            if args.segment == 0:
                seg_list2 = []
                for word in seg_list:
                    if word == '<num>':
                        seg_list2.append(word)
                    else:
                        seg_list2 += list(word)
                seg_list = seg_list2
            if len(seg_list) > 0:
                parsed_line.append(seg_list)
    print('Finished')


parser = argparse.ArgumentParser(description='Process lyrics')
parser.add_argument('--input', type=str, default='data/lyrics_v2.0.txt', help='input lyric file name')
parser.add_argument('--output', type=str, default='output/seg_lyrics.txt', help='output file name')
parser.add_argument('--format', type=str, default='custom')
parser.add_argument('--segment', type=int, default=1)
parser.add_argument('--maxlen', type=int, default=15)
args = parser.parse_args()
main(args)