#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: chenhe<hee0624@163.com>
# time: 2018-02-26
# version: 1.0



import urllib
from urllib.parse import urlparse
from urllib.parse import urljoin
from lxml import etree
import re
from bs4 import BeautifulSoup

import chardet
from fake_useragent import UserAgent

import domain
import comcode


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


def drop_null_list(list):
    """ 去除空列表"""
    new_list = []
    for item in list:
        if len(item.strip()) == 0:
            continue
        new_list.append(item)
    return new_list


def get_html(url):
    """获取网页的html源码"""
    ua = UserAgent()
    url_parse = urlparse(url)
    headers = {
        "User-Agent": ua.random,
        "Referer": "{}://{}".format(url_parse.scheme, url_parse.netloc),
    }
    req = urllib.request.Request(url=url, headers=headers)
    try:
        res = urllib.request.urlopen(req)
    except Exception as e:
        print(e)
        return ''
    text = res.read()
    code_detect = chardet.detect(text)['encoding']
    if code_detect:
        html = text.decode(code_detect, 'ignore')
    else:
        html = text.decode("utf-8", 'ignore')
    return html


def pretty_html(html):
    """html标准化补全非闭合标签"""
    soup = BeautifulSoup(html, 'html.parser')
    fixed_html = soup.prettify()
    return fixed_html


def get_links(url, html):
    """获得索引网页的所有url"""
    selector = etree.HTML(html)
    links = selector.xpath("//a/@href")
    for link in links:
        link = urljoin(url, link)
        lower_link = link.lower()
        if 'javascript' in lower_link:
            pass
        else:
            yield link


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
            return True
    else:
        return False


def count_uchar(str):
    """统计字符串当中字母和数字的个数"""
    num = count_num(str) + count_alphabet(str)
    return num


def count_alphabet(str):
    """统计字符串当中字母的个数"""
    num = 0
    for uchar in str:
        if is_alphabet(uchar):
            num += 1
    return num


def count_num(str):
    """统计字符串当中数字的个数"""
    num = 0
    for uchar in str:
        if is_number(uchar):
            num += 1
    return num


def seg_url(url):
    """切分url"""
    url = url.lower()
    url = url.replace(':', '/').replace('?', '/').replace('#', '/').replace('=', '/').replace('&', '/').replace('.', '/').replace('-', '/').replace('_', '/')
    url_item = drop_null_list(url.split('/'))
    return url_item


def drop_fix(str):
    """去除前缀"""
    str = str.replace('sz', '').replace('sh', '')
    return str


def is_noise(url):
    """判断url是否是干扰项"""
    url = url.lower()
    url_parse = urlparse(url)
    url_netloc = url_parse.netloc
    url_scheme = url_parse.scheme
    url_query = url_parse.query
    url_path = url_parse.path
    url_path = url_path.lstrip('/')
    if url.endswith('/'):
        return True
    # 去除非http协议网页网址
    if url_scheme not in {'http', 'https'}:
        return True
    # 去除文件
    pg_word = ['jpg', 'png', 'gif', 'pdf', 'txt', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'action', 'zip']
    for word in pg_word:
        if url_path.endswith(word):
            return True
    # 去除网站首页
    if not url_path:
        return True
    suffix_path = url_path.split('/')[-1]
    suffix_path = suffix_path.split('.')[0]
    suffix_path = suffix_path.split('_')[-1]
    uchar_num = count_uchar(suffix_path)
    alphabet_num = count_alphabet(suffix_path)
    num_num = count_num(suffix_path)
    if uchar_num < 4:
        return True
    if not url_query and alphabet_num < 10 and num_num == 0:
        return True
    home_word = ['index', 'home']
    for word in home_word:
        if word in url_path and not url_query and len(url_path.split('/')) < 3:
            return True
        if word in url_path and count_num(url_query) < 12:
            if count_num(url_query) < 4:
                return True
    # 去除干扰网页
    noise_word = ['newslist', 'user', 'login', 'logout', 'beian', 'register', 'iframe', 'account']
    for word in noise_word:
        if word in url_path:
            return True
    noise_word = ['bbs', 'video', 'tv', 'photo', 'help', 'member', 'about', 'vblog', 'flash', 'imgs', 'img']  # 'blog'
    for word in noise_word:
        if url_netloc.startswith(word):
            return True
        if url_path.startswith(word):
            return True
    else:
        return False


def is_domain(web, url):
    url_domain = get_domain(url)
    web_domain = get_domain(web)
    if not web_domain:
        return True
    else:
        if url_domain == web_domain:
            return True
        else:
            return False


def is_comcode(url):
    url_parse = urlparse(url)
    url_path = url_parse.path
    url_list = seg_url(url_path)
    for item in url_list:
        item = item.replace('s', '').replace('z', '').replace('h', '')
        if item:
            if item in comcode.comcode_set:
                return True
    else:
        return False


def get_domain(url):
    """获取网站一级域名"""
    url_parse = urlparse(url)
    url_netloc = url_parse.netloc
    url_netloc_list = url_netloc.split('.')
    while True:
        if not url_netloc_list:
            break
        last_item = url_netloc_list.pop()
        if last_item in domain.domain_set:
            continue
        else:
            return last_item
    else:
        return


def classify_news(url):
    """过滤新闻网址"""
    if is_time(url):
        return True
    else:
        if is_noise(url):
            return False
        else:
            for word in seg_url(url):
                if word in {'news', 'article', 'report', 'detail', 'newsid', 'newsd', 'xinwen', 'articleid', 'articled', 'content', 'view'}:
                    return True
                elif word in {'list', 'pid', 'zhuanti', 'live'}:
                    return False
                else:
                    pass
            else:
                return True


if __name__ == '__main__':
    url = 'http://www.mysteel.com/'
    html = get_html(url)
    html = pretty_html(html)
    for i in get_links(url, html):
        if is_domain(url, i):
            if classify_news(i):
                print(i, 'yes')
            else:
                print(i, 'no')
#