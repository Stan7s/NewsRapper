import requests
import bs4
import re


ARTIST_LIST = [
    'wang-yi-tai',
    'man-shu-ke',
    'an-quan-zhuo-lu',
    'j-sleeper-xing-gan-de-tuo-xie',
    'toy-wang-yi',
    'xiong-di-ben-se',
    'shen-lan-er-tong',
    'wu-hai-xiao',
    'jony-j',
    'hong-hua-hui',
    "'3bangz3bangz",
    'lil-jet',
    'po8',
    'higher-brothers',
    'pg-one'
]
def check_all_chinese(check_str):
    for ch in check_str:
        if ch == " ":
            continue
        if u'\u4e00' <= ch <= u'\u9fff':
            continue
        else:
            return False
    return True


def get_song_id_by_artist(artist):
    url = 'https://rapzh.com/artists/' + artist
    response = requests.get(url).text
    soup = bs4.BeautifulSoup(response,'html.parser')
    text = ""
    for i in soup.findAll(name='a', attrs = {'class':'css-ck8rn0'}):
        print(i['href'])
        get_lyric_by_song_id(i['href'])


def get_lyric_by_song_id(song_id):
    print(song_id)
    url = 'https://rapzh.com/songs/' + song_id
    lyric = ""
    response = requests.get(url).text
    if response.find("Not Found") > 0:
        return
    print("True")
    soup = bs4.BeautifulSoup(response, 'html.parser')
    lyrics = 'lyrics_v2.0.txt'
    with open(lyrics, 'a', encoding='UTF-8') as f:
        f.write("<song>\n")
        for i in soup.findAll(name='div', attrs={'class': 'css-8qbqv4'}):
            line = str(i.string)
            # print("【" + line + "】")
            if check_all_chinese(line):
                # print("True")
                f.write(line + '\n')
    return lyric


if __name__ == '__main__':
    for i in range(10000,11000):
        get_lyric_by_song_id(str(i))