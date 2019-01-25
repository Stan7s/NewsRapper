import matplotlib.pyplot as plt
import numpy as np
import jieba

with open('data/lyrics_v2.0.txt', encoding='utf8') as f:
    songs = f.read().split('<song>')
    print('number of songs:', len(songs))
    song_lines_cnt_list = []
    song_words_cnt_list = []
    line_len_list = []
    for song in songs:
        lines = song.splitlines()
        song_lines_cnt_list.append(len(lines))
        tot_words = 0
        for line in lines:
            seg_list = jieba.lcut(line)
            line_len_list.append(len(seg_list))
            tot_words += len(seg_list)
        song_words_cnt_list.append(tot_words)


plt.figure(1)
bins = np.arange(0, 60, 5)
plt.hist(song_lines_cnt_list, bins, facecolor="blue", edgecolor="black", alpha=0.7)
plt.xlabel("number")
plt.ylabel("count")
plt.title("Number of lines in a song")
plt.show()

plt.figure(2)
bins = np.arange(0, 60, 5)
plt.hist(song_words_cnt_list, bins, facecolor="blue", edgecolor="black", alpha=0.7)
plt.xlabel("number")
plt.ylabel("count")
plt.title("Number of words in a song")
plt.show()

plt.figure(3)
bins = np.arange(0, 60, 5)
plt.hist(line_len_list, bins, facecolor="blue", edgecolor="black", alpha=0.7)
plt.xlabel("number")
plt.ylabel("count")
plt.title("Number of words in a line")
plt.show()