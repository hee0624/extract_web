#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: chenhe<hee0624@163.com>
# time: 2017-11-30
# version: 1.0

import re


def drop_null(arg):
    """去除list或者str中的空白符"""
    if isinstance(arg, str):
        arg = re.sub('\s', '', arg, flags=re.S)
        return arg
    elif isinstance(arg, list):
        new_list = []
        for i in arg:
            i = i.strip()
            if i:
                new_list.append(i)
            else:
                continue
        return new_list
    else:
        return arg


def drop_mutil_br(str):
    """替换多行到一行"""
    str = re.sub(r'<br>|</br>', '\n', str)
    str = re.sub(r'\n\s+', '\n', str)
    return str


def drop_mutil_blank(str):
    """替换多行到一行"""
    str = re.sub(r'\xa0', ' ', str)
    str = re.sub(r'\s{2,}', ' ', str)
    return str


def tidy_time(str):
    """补全时间"""
    time_lst = str.split('-')
    day = time_lst[1] if len(time_lst) > 2 else ''
    if len(day) == 1:
        tmp = '-'.join(time_lst[2:])
        return f'{time_lst[0]}-0{day}-{tmp}'
    else:
        return str



