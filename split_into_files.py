# 把测试数据拆成很多文档（应该用一次就够了。。）
import pandas as pd

df = pd.read_csv('data/chinese_news.csv')
i = 1
for row in df.itertuples():
    if not pd.isnull(row.content):
        with open('data/news_content/news_%d.txt' % i, mode="w", encoding="utf8") as f:
            f.write(row.content)
            i += 1
