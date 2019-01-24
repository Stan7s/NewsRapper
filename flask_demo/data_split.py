import argparse
import numpy as np

parser = argparse.ArgumentParser(description='Random plit a document')
parser.add_argument('--input', type=str, default='output/seg_news.txt', help='input file name')
parser.add_argument('--output', type=str, default='output/news', help='output file name')
parser.add_argument('--ratio', type=float, default=0.1)
args = parser.parse_args()

with open(args.input, encoding='utf-8') as f:
    lines = f.readlines()
    n = len(lines)
    np.random.shuffle(lines)
    print('...shuffled')
    n1 = int(n * (1 - args.ratio))
    train = lines[:n1]
    dev = lines[n1:]
with open(args.output + '.train', encoding='utf-8', mode='w') as f:
    f.writelines(train)
    print('...train: %s.train' % args.output)
with open(args.output + '.dev', encoding='utf-8', mode='w') as f:
    f.writelines(dev)
    print('...dev: %s.dev' % args.output)
