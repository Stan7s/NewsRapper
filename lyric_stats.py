import matplotlib.pyplot as plt
import numpy as np

with open('data/lyrics_v1.2.txt', encoding='utf8') as f:
    lines = f.readlines()
    sub_lines = []
    for line in lines:
        sub_lines += line.split()
    lines_len = [len(line) for line in lines]
    sub_lines_len = [len(sub_line) for sub_line in sub_lines]

bins = np.arange(0, 60, 5)
plt.hist(lines_len, bins, alpha=0.5, label='lines')
plt.hist(sub_lines_len, bins, alpha=0.5, label='sub lines')
plt.legend(loc='upper right')
plt.xlabel("length")
plt.ylabel("count")
plt.title("Lyric Lines' Length")
plt.show()