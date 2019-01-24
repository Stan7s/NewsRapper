import re
import pandas as pd
import math


# https://github.com/fxsjy/jieba/issues/575
# 长句
resentencesp = re.compile('([\n﹒﹔﹖﹗．；。！？]["’”」』]{0,2}|：(?=["‘“「『]{1,2}|$))')
def splitsentence(sentence):
    s = sentence
    slist = []
    # print(s)
    for i in resentencesp.split(s):
        if resentencesp.match(i) and slist:
            slist[-1] += i
        elif i:
            slist.append(i)
    return slist


# 分句
resentencesp2 = re.compile(r'[ 　,:·\\/，﹒﹔﹖﹗．；。！？"’”："‘“—]')
def splitsentence2(sentence):
    s = sentence
    slist = []
    # print(s)
    for i in resentencesp2.split(s):
        if i:
            slist.append(i)
    return slist


# http://www.runoob.com/python3/python3-check-is-number.html
def is_number(s):
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
    #
    # return False


def to_number(s):
    try:
        f = float(s)
        return f
    except ValueError:
        pass

    try:
        import unicodedata
        f = unicodedata.numeric(s)
        return f
    except (TypeError, ValueError):
        pass


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


def read_from_csv(filename, threshold=0):
    df = pd.read_csv('data/chinese_news.csv')
    news_list = []
    for row in df.itertuples():
        # print(row)
        if not pd.isnull(row.content):
            if threshold > 0 and len(row.content) < threshold:
                continue
            news_list.append(row.content)
    return news_list


# https://luopuya.github.io/2014/03/29/Python%20%E5%88%A4%E6%96%AD%E6%B1%89%E5%AD%97%E5%AD%97%E7%AC%A6/
def ishan(text):
    # for python 3.x
    # sample: ishan('一') == True, ishan('我&&你') == False
    return all('\u4e00' <= char <= '\u9fff' for char in text)


def parse_segged_word(word, tokenize=True):
    if not word:
        return []
    if word == '\n' or word == '《' or word == '》' or word == '/' or word == '\\':
        return []
    if is_alpha(word):  # temp fix
        return []
    if is_number(word):
        if tokenize:
            return ['<num>']
        else:
            return [float2cn(word)]
    elif word[-1] == '%' and is_number(word[:-1]):
        if tokenize:
            return ['百分之', float2cn(word)]
        else:
            return ['百分之', '<num>']
    elif word == '+':
        return ['加']
    elif word in '、《》（）() ﹒﹔﹖﹗．；。！？"’”」』"‘“「『@ 　,:·\\/，﹒﹔﹖﹗．；。！？’”："‘“—':  # 删除标点
        return []
    elif not ishan(word):
        return []
    else:
        return [word]


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
    if abs(f) <= 1e-6:
        return pre + num2cn(i, traditional)
    return pre + num2cn(i, traditional) + '点' + num2cn(int(f + 0.5), traditional, True)