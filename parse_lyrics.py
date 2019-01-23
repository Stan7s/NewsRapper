# 把歌词转成训练数据形式

import argparse
import jieba
import thulac
from hanziconv import HanziConv


def main(args):
    with open(args.input, encoding='utf8') as f:
        lines = f.read().split()
        if args.format == 'lines':
            lines.append('<song>')
    parsed_line = []
    thu1 = thulac.thulac(seg_only=True)
    with open(args.output, encoding='utf8', mode='w') as f:
        i = 0
        n = len(lines)
        for line in lines:
            if args.format == 'lines':
                line = HanziConv.toSimplified(line)
            if i % 100 == 0:
                print('status: %d/%d' % (i, n))
            i += 1
            if line == '<song>':
                if len(parsed_line) == 0:
                    continue
                n = len(parsed_line)
                # 控制每句总长度为15
                for i in range(n):
                    l = len(parsed_line[i])
                    if l > 15:
                        continue
                    ctrl_list = parsed_line[i]
                    for k in range(i+1, n+1):
                        if k == n or l + len(parsed_line[k]) + 1 > 20:
                            f.write(' '.join(ctrl_list) + '\n')
                            break
                        ctrl_list.append('<lbreak>')
                        ctrl_list += parsed_line[k]
                        l += len(parsed_line[k]) + 1
                parsed_line = []
                continue
            # parsed_line.append(jieba.lcut(line))
            seg_list = thu1.cut(line)
            seg_list = [t[0] for t in seg_list]
            parsed_line.append(seg_list)
    print('Finished')

parser = argparse.ArgumentParser(description='Process a document')
parser.add_argument('--input', type=str, default='data/lyrics_v1.3.txt', help='input lyric file name')
parser.add_argument('--output', type=str, default='output/parsed_lyrics.txt', help='output file name')
parser.add_argument('--format', type=str, default='custom')
args = parser.parse_args()
main(args)