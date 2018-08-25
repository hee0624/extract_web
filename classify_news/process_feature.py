#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: chenhe<hee0624@163.com>
# time: 2018-07-05
# version: 1.0


from urllib.parse import urlparse
import re
import os
import classify_news
def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u'\u0030' and uchar <= u'\u0039':
        return True
    else:
        return False


def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False



# 是否含有时间项
def is_time(url):
    """判断字符串是否含有时间项"""
    time_rules = [
        '\d\d\d\d\d\d\d{1,2}',
        '\d\d\d\d-\d\d-\d{1,2}',
        '\d\d\d\d-\d\d/\d{1,2}',
        '\d\d\d\d/\d\d/\d{1,2}',
        '\d\d\d\d/\d\d-\d{1,2}',
        '\d\d\d\d/\d\d\d{1,2}',
        '\d\d\d\d-\d\d\d{1,2}',
        '\d\d\d\d\d\d-\d\{1,2}',
        '\d\d\d\d\d\d/\d{1,2}',
        '\d{1,2}/\d\d\d\d/\d\d',
        '\d\d/\d\d\d\d/\d{1,2}',
        '\d\d\d\d-\d\d',
        '\d\d\d\d/\d\d',
        '\d\d\d\d\d\d-\d{1,2}',
        '\d\d/\d\d\d\d',
        '\d\d-\d\d\d\d'
    ]
    url_parse = urlparse(url)
    url_path = url_parse.path
    for time_rule in time_rules:
        if re.search(time_rule, url_path):
            flag = True
            break
    else:
        flag = False
    return flag


# 是否含有反斜杠
def is_slant(url):
    if url.endswith('/'):
        flag = True
    else:
        flag = False
    return flag


# 协议是否是http/https
def is_http(url):
    url = url.lower()
    url_parse = urlparse(url)
    url_scheme = url_parse.scheme
    if url_scheme not in {'http', 'https'}:
        flag = True
    else:
        flag = False
    return flag


# 是否是无关格式
def is_noise_ext(url):
    url = url.lower()
    url_parse = urlparse(url)
    url_path = url_parse.path
    exts = ['jpg', 'png', 'gif', 'pdf', 'txt', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'action', 'zip']
    for ext in exts:
        if url_path.endswith(ext):
            flag = True
            break
    else:
        flag = False
    return flag


# 是否含有噪声文字
def is_noise_word(url):
    url = url.lower()
    url_parse = urlparse(url)
    url_path = url_parse.path
    url_netloc = url_parse.netloc
    noise_word_lst = ['newslist', 'user', 'login', 'logout', 'beian', 'register', 'iframe', 'account','bbs', 'video', 'tv', 'photo', 'help', 'member', 'about', 'vblog', 'flash', 'imgs', 'img']
    for word in noise_word_lst:
        if url_netloc.startswith(word) or url_path.startswith(f'/{word}'):
            flag = True
            break
    else:
        flag = False
    return flag


# 计算路径长度
def count_path_length(url):
    url_parse = urlparse(url)
    url_path = url_parse.path
    return len(url_path.split('/'))

# 计算home/index索引
def cal_home_pos(url):
    pass


# 计算文件名长度
def count_file_length(url):
    url_parse = urlparse(url)
    url_path = url_parse.path
    url_path = os.path.splitext(url_path)[0]
    filename = url_path.split('/')[-1]
    return len(filename)


# 计算文件名英文字符的个数
def count_alphabet(url):
    url_parse = urlparse(url)
    url_path = url_parse.path
    url_path = os.path.splitext(url_path)[0]
    filename = url_path.split('/')[-1]
    num = 0
    for uchar in filename:
        if is_alphabet(uchar):
            num += 1
    return num


# 计算文件名数字的个数
def count_num(url):
    url_parse = urlparse(url)
    url_path = url_parse.path
    url_path = os.path.splitext(url_path)[0]
    filename = url_path.split('/')[-1]
    num = 0
    for uchar in filename:
        if is_number(uchar):
            num += 1
    return num


# 是否含有查询项
def is_query(url):
    url_parse = urlparse(url)
    url_query = url_parse.query
    if url_query:
        return True
    else:
        return False


def process_feature(url):
    features = []
    features.append(url)

    features.append(1) if is_time(url) else features.append(0)
    features.append(1) if is_slant(url) else features.append(0)
    features.append(1) if is_http(url) else features.append(0)
    features.append(1) if is_noise_ext(url) else features.append(0)
    features.append(1) if is_noise_word(url) else features.append(0)
    features.append(1) if is_query(url) else features.append(0)
    features.append(count_file_length(url))
    features.append(count_alphabet(url))
    features.append(count_num(url))
    features.append(count_path_length(url))

    features.append(1) if classify_news.classify_news(url) else features.append(0)
    return features


def run():
    import time
    std = time.time()
    import xlwt
    workbook1 = xlwt.Workbook(encoding='utf-8')
    worksheet1 = workbook1.add_sheet('sheet1')
    workbook2 = xlwt.Workbook(encoding='utf-8')
    worksheet2 = workbook2.add_sheet('sheet1')
    with open('20180705-corpus.txt', 'r') as fp:
        for index, line in enumerate(fp):
            line = line.strip()
            data = process_feature(line)
            print(data)
            if index < 50000:
                for sub_index, item in enumerate(data):
                    worksheet1.write(index, sub_index, item)
            else:
                for sub_index, item in enumerate(data):
                    worksheet2.write(index-50000, sub_index, item)
    workbook1.save('20180805-data1.xls')
    workbook2.save('20180805-data2.xls')
    print(f'耗时{time.time()-std}')

if __name__ == '__main__':
    run()