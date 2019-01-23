# 对一个文档中的句子进行处理

import argparse
import re
import jieba
import pypinyin
import math
import numpy as np
import matplotlib.pyplot as plt

resentencesp = re.compile('[ ,:·，﹒﹔﹖﹗．；。！？"’”："‘“—]')


# https://zouhualong.oschina.io/pages/blog/python/Python-%E6%95%B0%E5%AD%97%E8%BD%AC%E6%B1%89%E5%AD%97
def num2cn(number, traditional=False, direct=False):
    '''数字转化为中文
    参数：
        number: 数字
        traditional: 是否使用繁体
    '''
    chinese_num = {
        'Simplified': ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九'],
        'Traditional': ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    }
    chinese_unit = {
        'Simplified': ['个', '十', '百', '千'],
        'Traditional': ['个', '拾', '佰', '仟']
    }
    extra_unit = ['', '万', '亿']

    if traditional:
        chinese_num = chinese_num['Traditional']
        chinese_unit = chinese_unit['Traditional']
    else:
        chinese_num = chinese_num['Simplified']
        chinese_unit = chinese_unit['Simplified']

    num_cn = []

    # 数字转换成字符列表
    num_list = list(str(number))

    # 反转列表，个位在前
    num_list.reverse()

    # 数字替换成汉字
    for num in num_list:
        num_list[num_list.index(num)] = chinese_num[int(num)]

    # print('num2cn:', number)
    if direct:
        num_list.reverse()
        return ''.join(num_list)

    # 每四位进行拆分，第二个四位加“万”，第三个四位加“亿”
    for loop in range(len(num_list)//4+1):
        sub_num = num_list[(loop * 4):((loop + 1) * 4)]
        if not sub_num:
            continue

        # 是否增加额外单位“万”、“亿”
        if loop > 0 and 4 == len(sub_num) and chinese_num[0] == sub_num[0] == sub_num[1] == sub_num[2] == sub_num[3]:
                use_unit = False
        else:
            use_unit = True

        # 合并数字和单位，单位在每个数字之后
        # from itertools import chain
        # sub_num = list(chain.from_iterable(zip(chinese_unit, sub_num)))
        sub_num = [j for i in zip(chinese_unit, sub_num) for j in i]

        # 删除第一个单位 '个'
        del sub_num[0]

        # “万”、“亿”中如果第一位为0则需加“零”: 101000，十万零一千
        use_zero = True if loop > 0 and chinese_num[0] == sub_num[0] else False

        if len(sub_num) >= 7 and chinese_num[0] == sub_num[6]:
            del sub_num[5]  # 零千 -> 零
        if len(sub_num) >= 5 and chinese_num[0] == sub_num[4]:
            del sub_num[3]  # 零百 -> 零
        if len(sub_num) >= 3 and chinese_num[0] == sub_num[2]:
            del sub_num[1]  # 零十 -> 零
        if len(sub_num) == 3 and chinese_num[1] == sub_num[2]:
            del sub_num[2]  # 一十开头的数 -> 十

        # 删除末位的零
        while len(num_list) > 1 and len(sub_num) and chinese_num[0] == sub_num[0]:
            del sub_num[0]

        # 增加额外的“零”
        if use_zero and len(sub_num) > 0:
            num_cn.append(chinese_num[0])

        # 增加额外单位“万”、“亿”
        if use_unit:
            num_cn.append(extra_unit[loop])

        num_cn += sub_num

    # 删除连续重复数据：零，只有零会重复
    num_cn = [j for i, j in enumerate(num_cn) if i == 0 or j != num_cn[i-1]]
    # 删除末位的零，最后一位为 extra_unit 的 ''
    if len(num_list) > 1 and len(num_cn) > 1 and chinese_num[0] == num_cn[1]:
        del num_cn[1]

    # 反转并连接成字符串
    num_cn.reverse()
    num_cn = ''.join(num_cn)

    return(num_cn)


def float2cn(number, traditional=False):
    '''
    浮点数转中文
    :param number:
    :param traditional:
    :return:
    '''
    f = float(number)
    pre = ''
    if f < 0:
        f = -f
        pre = '负'
    if math.fabs(f - int(f)) < 1e-9:
        return pre + num2cn(number, traditional)
    i = int(f)
    f = f - i
    while math.fabs(f - int(f + 0.5)) >= 1e-9:
        f = f * 10
    return pre + num2cn(i, traditional) + '点' + num2cn(int(f + 0.5), traditional, True)


def split_sentence(sentence):
    '''
    将一段话切割成分句
    :param sentence: 文段
    :return: 切割结果
    '''
    s = sentence
    slist = []
    # print(s)
    for i in resentencesp.split(s):
        if resentencesp.match(i) and slist:
            slist[-1] += i
        elif i:
            slist.append(i)
    return slist


# http://www.runoob.com/python3/python3-check-is-number.html
def is_number(s):
    '''
    判断字符串是否表示数字
    :param s:
    :return:
    '''
    try:
        float(s)
        return True
    except ValueError:
        pass

    # try:
    #     import unicodedata
    #     unicodedata.numeric(s)
    #     return True
    # except (TypeError, ValueError):
    #     pass

    return False


# https://leowood.github.io/2018/05/19/Python3%E5%88%A4%E6%96%AD%E5%AD%97%E7%AC%A6%E4%B8%AD%E8%8B%B1%E6%96%87%E6%95%B0%E5%AD%97%E7%AC%A6%E5%8F%B7/
def is_alphabet(char):
    '''
    判断字符是否为英文字母
    :param char:
    :return:
    '''
    if (char >= '\u0041' and char <= '\u005a') or (char >= '\u0061' and char <= '\u007a'):
        return True
    else:
        return False


def is_alpha(s):
    '''
    判断字符串是否只包含英文字母
    :param s:
    :return:
    '''
    for ch in s:
        if not is_alphabet(ch):
            return False
    return True


class Zh_Sent(object):
    def __init__(self, str, seg_list, pinyin_list, yunmu_list, tone_list):
        self.str = str
        self.seg_list = seg_list
        self.pinyin_list = pinyin_list
        self.yunmu_list = yunmu_list
        self.tone_list = tone_list
        self.length = 0
        for seg in self.seg_list:
            self.length += len(seg)

    def get_last_yunmu(self):
        return self.yunmu_list[-1][-1]

    def get_last_pinyin(self):
        return self.pinyin_list[-1][-1]

    def get_last_tone(self):
        return self.tone_list[-1][-1]


# https://stackoverflow.com/questions/2460177/edit-distance-in-python
def calc_edit_distance(s1, s2):
    '''
    计算s1和s2之间的编辑距离
    :param s1:
    :param s2:
    :return:
    '''
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def compare_sentences(sentences):
    '''
    计算两句话的相似度
    :param sentences:
    :return:
    '''
    n = len(sentences)
    length_similarities = [] # 长度接近程度
    tail_similarities = []  # 最后一个字押韵的程度
    total_similarities = []  # 节奏相似度
    edit_distance = []
    for i in range(n):
        length_similarities.append([])
        tail_similarities.append([])
        total_similarities.append([])
        edit_distance.append([])
        for j in range(n):
            # 计算这两个句子的相似度
            # 编辑距离
            edit_distance[-1].append(calc_edit_distance(sentences[i].str, sentences[j].str))
            # 长度的相似度？
            l1 = sentences[i].length
            l2 = sentences[j].length
            m = min(l1, l2)
            length_similarities[-1].append((l1 + l2 - 2*m) / (l1 + l2))
            # 计算最后一个字的相似度？
            if sentences[i].get_last_pinyin() == sentences[j].get_last_pinyin():
                tail = 1.0
            elif sentences[i].get_last_yunmu() == sentences[j].get_last_yunmu():
                tail = 0.7
            elif sentences[i].get_last_tone() == sentences[j].get_last_tone():
                tail = 0.2
            else:
                tail = 0.0
            tail_similarities[-1].append(tail)
            # 从每个字开始的节奏的匹配？
            # 应该取最大值而不是所有值。
            total = 0
            for k in range(len(sentences[j].seg_list)):
                # sentences[i][0]开始尝试和sentences[j][k]匹配
                i1 = 0
                i2 = k
                cnt = 0
                sum1 = len(sentences[i].seg_list[i1])
                sum2 = len(sentences[j].seg_list[i2])
                while i1 < len(sentences[i].seg_list) and i2 < len(sentences[j].seg_list):
                    if sum1 < sum2:
                        i1 += 1
                        if i1 >= len(sentences[i].seg_list):
                            break
                        sum1 += len(sentences[i].seg_list[i1])
                    elif sum1 > sum2:
                        i2 += 1
                        if i2 >= len(sentences[j].seg_list):
                            break
                        sum2 += len(sentences[j].seg_list[i2])
                    else:
                        cnt += 1
                        i1 += 1
                        i2 += 1
                        if i1 >= len(sentences[i].seg_list) or i2 >= len(sentences[j].seg_list):
                            break
                        sum1 = len(sentences[i].seg_list[i1])
                        sum2 = len(sentences[j].seg_list[i2])
                total = max(cnt, total)
            total_similarities[-1].append(total * 2 / (len(sentences[i].seg_list) + len(sentences[j].seg_list)))

    return np.array(edit_distance), np.array(length_similarities), np.array(tail_similarities), np.array(total_similarities)


def find_path(graph, threshold):
    n = len(graph)
    f = np.zeros(n, dtype=np.int)
    last = np.zeros(n, dtype=np.int)
    f[0] = 1
    last[0] = -1
    maxlen = 0
    ans = -1
    for i in range(1, n):
        f[i] = 1
        for j in range(0, i):
            if f[j] + 1 > f[i] and graph[i, j] >= threshold:
                last[i] = j
                f[i] = f[j] + 1
        if f[i] > maxlen:
            maxlen = f[i]
            ans = i
    path = []
    while not ans == -1:
        path.append(ans)
        ans = last[ans]
    path.reverse()
    return path


# 把一个过长的句子分成几段
def cut_sentences(sentence, force=-1):
    if sentence.length <= 12 and force == -1:
        return [sentence]
    sent_list = []
    seg_list = []
    pinyin_list = []
    yunmu_list = []
    tone_list = []
    length = 0
    n = len(sentence.seg_list)
    # print('/'.join(sentence.seg_list))
    for i in range(n + 1):
        # print(length)
        if i == n or (force == -1 and length >= 6 or not force == -1 and length >= force):
            if force == -1 and length >= 6 or not force == -1 and length == force:
                sent_list.append(Zh_Sent(''.join(seg_list), seg_list, pinyin_list, yunmu_list, tone_list))
            seg_list = []
            pinyin_list = []
            yunmu_list = []
            tone_list = []
            length = 0
            if i == n:
                break
        length += len(sentence.seg_list[i])
        seg_list.append(sentence.seg_list[i])
        pinyin_list.append(sentence.pinyin_list[i])
        yunmu_list.append(sentence.yunmu_list[i])
        tone_list.append(sentence.tone_list)
    return sent_list


def split_article(article):
    '''
    处理一整篇文章
    :param article: 文章
    :return:
    '''
    slist = split_sentence(article)
    print('句子（分句）总数：', len(slist))

    sentences = []
    for s in slist:
        s = s.strip()
        if len(s) == 0:  # patch for empty
            continue
        if len(s) < 5:  # 删除词数太少的句子
            continue
        seg_list = jieba.lcut(s)  # list cut
        if len(seg_list) == 0:  # patch for empty
            continue
        seg_list2 = []
        # 筛掉\n之类奇怪的东西，同时去掉标点符号
        for word in seg_list:
            if word == '\n' or word == '《' or word == '》':
                continue
            if is_number(word):
                # print(word)
                word = float2cn(word)  # queer fix
            if word[-1] == '%' and is_number(word[:-1]):
                seg_list2.append('百分之')
                word = float2cn(word[:-1])  # queer fix
            if word == '+':
                word = '加'
            if word in '、《》（）()':  # 删除标点
                continue
            if is_alpha(word):  # temp fix
                # print('判断为英文：', word)
                # word = '英文'
                pass
            seg_list2.append(word)
        if len(seg_list2) == 0:  # patch for empty
            continue
        pinyin_list = []
        yunmu_list = []
        tone_list = []
        for word in seg_list2:
            pinyin_list.append(pypinyin.lazy_pinyin(word))
            yunmu_list.append(pypinyin.lazy_pinyin(word, style=pypinyin.Style.FINALS))
            tones = pypinyin.lazy_pinyin(word, style=pypinyin.Style.TONE3)
            for i in range(len(tones)):
                if not is_alphabet(tones[i][-1]):
                    tones[i] = int(tones[i][-1])
                else:
                    tones[i] = 0
            tone_list.append(tones)
        # print('/'.join(seg_list2))
        # print(str(pinyin_list))
        # print(str(yunmu_list))
        # print(str(tone_list))
        # 把过长的句子拆开
        sent = cut_sentences(Zh_Sent(s, seg_list2, pinyin_list, yunmu_list, tone_list), force=args.force_same)
        sentences += sent

    for i in range(len(sentences)):
        print("sentence %d: %s" % (i, '/'.join(sentences[i].seg_list)))

    # 计算句子的相似度
    edit_distance, length_similarities, tail_similarities, total_similarities = compare_sentences(sentences)
    # edit distance
    too_similiar_mask = np.greater(edit_distance, 1).astype(np.float)
    # 值是随便取的
    similarities = 0.5 * length_similarities + 0.4 * tail_similarities + 0.1 * total_similarities
    similarities = np.multiply(similarities, too_similiar_mask)

    # 可视化
    img = plt.imshow(similarities, interpolation='nearest', cmap='gray', origin="lower")
    # make a color bar
    plt.colorbar(img, cmap='gray')
    plt.show()

    # 二分答案 + DP找总长度大于20的句子
    l = 0.0
    r = 1.0
    while r - l > 1e-6:
        m = (l + r) / 2.0
        path = find_path(similarities, m)
        if len(path) >= 20:
            l = m
        else:
            r = m
    print('最大相似度：', m)
    print(str(path))
    selected = []
    for i in path:
        selected.append(''.join(sentences[i].seg_list))
    return selected


parser = argparse.ArgumentParser(description='Process a document')
parser.add_argument('--filename', type=str, help='Chinese utf8 file name')
parser.add_argument('--force_same', type=int, default=-1, help='Force each segment to have same length')
args = parser.parse_args()
with open(args.filename, encoding="utf8") as f:
    article = f.read()
    # print(article)
    selected = split_article(article)
    print('\n'.join(selected))
