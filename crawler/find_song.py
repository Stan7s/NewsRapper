import requests
import bs4
import re


ARTIST_LIST = [
    'wang-yi-tai',
    'man-shu-ke',
    'an-quan-zhuo-lu',
    'j-sleeper-xing-gan-de-tuo-xie',
    'toy-wang-yi',
    'xiong-di-ben-se'
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
    url = 'https://rapzh.com' + song_id
    lyric = ""
    response = requests.get(url).text
    soup = bs4.BeautifulSoup(response, 'html.parser')
    lyrics = 'lyrics_v1.2.txt'
    with open(lyrics, 'a', encoding='UTF-8') as f:
        f.writelines("<song>\n")
        for i in soup.findAll(name='div', attrs={'class': 'css-8qbqv4'}):
            line = str(i.string)
            # print("【" + line + "】")
            if check_all_chinese(line):
                # print("True")
                f.write(line + '\n')
    return lyric


if __name__ == '__main__':
    for artist in ARTIST_LIST:
        get_song_id_by_artist(artist)