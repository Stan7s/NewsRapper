import csv
import os
import numpy as np
import random
import requests

# name of data file
news_file = 'chinese_news.csv'


def read_data():
    news_data = []
    with open(news_file, 'r', encoding='UTF-8') as csvfile:
        print("successfully opened.")
        csv_reader = csv.reader(csvfile)
        news_header = next(csv_reader)
        for row in csv_reader:
            news_data.append(row)
    news_data = np.array(news_data)
    news_header = np.array(news_header)
    print(news_data.shape)
    print(news_header.shape)
    return news_header, news_data


def remove_short_news(news_data):
    long_news = []
    for row in news_data:
        if row[1] == '详细全文' and len(row[3]) >= 500:
            long_news.append(row)
    print(len(long_news))
    return long_news


def purify(news_data):
    result = []
    with open('long_news.txt', 'w', encoding='utf-8') as f:
        for news in news_data:
            if news[3].find('习近平') > 0:
                continue
            else:
                print(news[3])
                result.append(news[3] + '<news>\n')
                f.write(news[3] + '<news>\n')
        print(len(result))
    return result

if __name__ == '__main__':
    news_header, news_data = read_data()
    print(news_header)
    long_news = remove_short_news(news_data)
    result = purify(long_news)

    # remove_short_news(news_header, news_data)
