import csv
import os
import numpy as np
import random
import requests

# name of data file
news_file = 'data/chinese_news.csv'


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


def remove_short_news(news_header, news_data):
    long_news = []
    for row in news_data:
        if row[1] == '详细全文' and len(row[3]) >= 500:
            long_news.append(row)
    print(len(long_news))
    return long_news


if __name__ == '__main__':
    news_header, news_data = read_data()
    print(news_header)
    remove_short_news(news_header, news_data)
