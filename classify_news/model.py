#! /user/bin/env python
# coding:utf-8

from sklearn import svm
from sklearn.externals import joblib

from sklearn import tree
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import graphviz
import process_feature



def load_data():
    import xlrd
    xls_path = 'corpus/20180805-data1.xls'
    book = xlrd.open_workbook(xls_path)
    sheet = book.sheet_by_index(0)
    nrows = sheet.nrows
    nrows = 2000
    head = 0
    data = []
    target = []
    for row in range(head,nrows):
        row_data = sheet.row_values(row)
        data.append(row_data[1: -2])
        target.append(row_data[-1])
    return np.array(data), np.array(target)



def cal_rule_score():
    import xlrd
    xls_path = 'corpus/20180805-data1.xls'
    book = xlrd.open_workbook(xls_path)
    sheet = book.sheet_by_index(0)
    nrows = sheet.nrows
    nrows = 2000
    head = 0
    data = []
    col_num = 0
    err_num =0
    for row in range(head,nrows):
        row_data = sheet.row_values(row)
        if row_data[-2] == row_data[-1]:
            col_num += 1
        else:
            err_num += 1
    print(f'thr rule classifier is {col_num/(col_num+err_num)}')


# 训练模型
def train_model():
    iris_x, iris_y = load_data()
    indices = np.random.permutation(len(iris_x))
    x_train = iris_x[indices[:-1000]]
    y_train = iris_y[indices[:-1000]]
    x_test = iris_x[indices[-1000:]]
    y_test = iris_y[indices[-1000:]]
    clfs = {
        'random_forest': RandomForestClassifier(n_estimators=50),
        'svm': svm.SVC(),
        'tree': tree.DecisionTreeClassifier()
    }
    for clf_key, clf_value in clfs.items():
        clf = clf_value
        clf.fit(x_train, y_train)
        # print(clf.predict(x_test))
        # print(y_test)
        # print(clf.predict_proba(x_test))
        score = clf.score(x_test, y_test)
        # joblib.dump(clf, f'models/{clf_key}_model.m')
        print(f'the {clf_key} classifier is : {score}')
    # cal_rule_score()


def prdit_url():
    clf = joblib.load('models/tree_model.m')
    features = []
    url = 'http://news.youth.cn/sz/201807/t20180705_11661457.htm'
    url = 'https://ent.china.com/star/gang/11057089/20180705/32635298.html?newsbaidu'
    # url = 'http://news.baidu.com/ent'
    # url = 'https://www.lmjx.net/sanzhuangshuiniyunshuche/'
    # url = 'https://zj.lmjx.net/detail_NDA00---.html'
    # url = 'https://zj.lmjx.net/prise_list_1608414.html'
    # url = 'https://zj.lmjx.net/Nav_Brand.html'
    url = 'http://www.cs.com.cn/xwzx/xwzt/20170217/'
    url = 'http://news.cn/fortune/gsbd/ssssd.html'
    url = 'https://www.baidu.com/s?wd=%E8%B7%AF%E9%9D%A2%E6%9C%BA%E6%A2%B0%E7%BD%91'
    url = 'https://www.sohu.com/a/226265476_609569'
    url = 'https://blog.csdn.net/a819825294/article/details/51206410'
    url = 'http://www.dvbcn.com/t/%E9%80%B8%E4%BA%91%E7%A7%91%E6%8A%80'
    # url = 'http://news.luosi.com/news-2.html'
    url = 'http://news.luosi.com/articles-11205.html'

    features.append(1) if process_feature.is_time(url) else features.append(0)
    features.append(1) if process_feature.is_slant(url) else features.append(0)
    features.append(1) if process_feature.is_http(url) else features.append(0)
    features.append(1) if process_feature.is_noise_ext(url) else features.append(0)
    features.append(1) if process_feature.is_noise_word(url) else features.append(0)
    features.append(1) if process_feature.is_query(url) else features.append(0)
    features.append(process_feature.count_file_length(url))
    features.append(process_feature.count_alphabet(url))
    features.append(process_feature.count_num(url))
    features.append(process_feature.count_path_length(url))
    print(clf.predict([features]))
if __name__ == '__main__':
    train_model()
    # prdit_url()