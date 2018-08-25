#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: chenhe<hee0624@163.com>
# time: 2017-11-30
# version: 1.0

import copy
import re
from collections import Counter
from operator import itemgetter

from lxml import etree

from handle_html import *
import nlp
import utils
from get_html import get_html


class NewsParser:

    def __init__(self):
        self.score = 6
        self.length = 5

    def _cal_score(self, text):
        """计算兴趣度"""
        if "。" not in text:
            if "，" in text:
                return 0
            else:
                return -1
        else:
            score = text.count('，') + 1
            score += text.count(',') + 1
            score += text.count('；')
            score += text.count('。')
            return score

    def _line_div(self, html):
        """线性重构html代码"""
        html = re.sub("</?div>|</?table>", "</div><div>", html, flags=re.I)
        html = html.replace('</div>', '', 1)
        index = html.rfind('<div>')
        html = html[:index] + html[index:].replace('<div>', '', 1)
        return html

    def _line_p(self, text):
        """p标签变成2层嵌套结构，第二层为线性"""
        text_list = list()
        text = re.sub(r'</?p\s?.*?>', r'</p><p class="news_body">', text, flags=re.I | re.S)
        text = text.replace('</p>', '', 1)
        index = text.rfind('<p>')
        text = text[:index] + text[index:].replace('<p>', '', 1)
        text = '<p class="news_head">{0}</p>'.format(text)
        return text

    def _extract_paragraph(self, html):
        """
        通过计算兴趣度得分，抽取聚类段落集和吸收段落集
        :param html:
        :return: tuple
        """
        cluster_para = {}
        absorb_para = {}
        for index, div_str in enumerate(re.findall("<div>(.*?)</div>", html, flags=re.S | re.I)):
            if len(div_str.strip()) == 0:
                continue
            para_str = div_str.strip()
            score = self._cal_score(para_str)
            if score > self.score:
                cluster_para[index] = [para_str, score]
            else:
                absorb_para[index] = [para_str, score]
        return cluster_para, absorb_para

    def _extract_feature(self, para_dict):
        """
        抽取聚类段落集里的特征，获得得分最高的div下的p最多的属性值
        :param para_dict:
        :return:
        """
        c = Counter()
        index, text = max(para_dict.items(), key=lambda asd: asd[1][1])
        # print('-------------抽取最大特征段落集----------------')
        # print(index)
        # print(text[0])
        feature_list = re.findall("(<p.*?>)", text[0], flags=re.I | re.S)
        for feature in feature_list:
            c[feature] += 1
        if c.most_common(1):
            feature, amount = c.most_common(1)[0]
        else:
            feature = ''
        # self.logger.debug(feature)
        # print('-------------抽取最大特征----------------')
        feature = feature.replace('(', '\(').replace(')', '\)')
        # print(feature)
        return index, feature

    def _gen_skeleton(self, para_dict, index, feature):
        """ 聚类段落集聚类生成生成正文脉络集合"""
        skeleton_dict = {}
        num_list = []
        if not feature:
            skeleton_dict[index] = para_dict[index]
            return skeleton_dict
        for num in para_dict.keys():
            num_list.append(num)
        num_list = sorted(num_list)
        od = num_list.index(index)
        f_list = num_list[0:od]
        l_list = num_list[od:len(num_list)]
        # 向后聚类
        while l_list:
            tmp = l_list.pop(0)
            length = abs(tmp - index)
            if length < self.length:
                if re.match(r".*?{0}".format(feature), para_dict[tmp][0], flags=re.S | re.I):
                    skeleton_dict[tmp] = para_dict[tmp]
            index = tmp
        # 向前聚类
        while f_list:
            tmp = f_list.pop()
            length = abs(index - tmp)
            if length < self.length:
                if re.match(r".*?{0}".format(feature), para_dict[tmp][0], flags=re.S):
                    skeleton_dict[tmp] = para_dict[tmp]
            index = tmp
        return skeleton_dict

    def _absorb_text(self, skeleton_dict, para_dict):
        """从伪噪声段落吸收噪声段落"""
        content_dict = skeleton_dict
        sk_list = skeleton_dict.keys()
        pa_list = para_dict.keys()
        sk_list = sorted(sk_list)
        pa_list = sorted(pa_list)
        heads = []
        middle = []
        tail = []
        for each in pa_list:
            if each < sk_list[0]:
                heads.append(each)
            if each > sk_list[-1]:
                tail.append(each)
            if (each >= sk_list[0]) and (each <= sk_list[-1]):
                middle.append(each)
        while heads:
            tmp = heads.pop()
            index = sk_list[0]
            if abs(tmp - index) < self.length:
                if para_dict[tmp][1] * 2 > self.score:
                    content_dict[tmp] = para_dict[tmp]
            else:
                break
        while tail:
            tmp = tail.pop(0)
            index = sk_list[-1]
            if abs(tmp - index) < self.length:
                if para_dict[tmp][1] * 2 > self.score:
                    content_dict[tmp] = para_dict[tmp]
            else:
                break
        while middle:
            tmp = middle.pop()
            if para_dict[tmp][1] * 2 > self.score:
                content_dict[tmp] = para_dict[tmp]
        return content_dict

    def _substring(self, text):
        text = self._line_p(text)
        text = pretty_html(text)
        selector = etree.HTML(text)
        xpath_result = selector.xpath('//p')
        if len(xpath_result) == 1:
            sub_string = xpath_result[0].xpath('string(.)')
            sub_string = utils.drop_mutil_br(sub_string)
        else:
            text_list = []
            xpath_result = selector.xpath('//p[@class="news_body"]')
            for item in xpath_result:
                p_string = item.xpath('string(.)').strip()

                if not p_string:
                    continue
                p_string = utils.drop_null(p_string)
                text_list.append(p_string)
            if text_list:
                sub_string = '\n'.join(text_list)
            else:
                sub_string = ''
        return sub_string

    def _pretty_text(self, index_content_list):
        contents = list()
        for each in index_content_list:
            sub_text = self._substring(each[1][0])
            if not sub_text:
                continue
            else:
                contents.append(sub_text)
        text = "\n".join(contents)
        return text

    def extract_news(self, html):
        html = handle_html(html)
        html = self._line_div(html)
        head_index = 0
        tail_index = 10000000
        cluster_para, absorb_para = self._extract_paragraph(html)
        if cluster_para:
            index, feature = self._extract_feature(cluster_para)
            skeleton_dict = self._gen_skeleton(cluster_para, index, feature)
            if skeleton_dict:
                if absorb_para:
                    content_dict = self._absorb_text(skeleton_dict, absorb_para)
                else:
                    content_dict = skeleton_dict
                index_content_list = sorted(content_dict.items(), key=itemgetter(0))

                top_div_list = list()
                tail_div_list = list()
                top_text = ''
                tail_text = ''
                head_index = index_content_list[0][0]
                tail_index = index_content_list[-1][0]
                for ind, each_div in enumerate(re.findall("<div>(.*?)</div>", html, flags=re.S)):
                    # if ind >= index:
                    #     break
                    if ind < head_index:
                        top_text += each_div
                        top_div_list.append((ind, each_div))
                    elif ind > tail_index:
                        tail_text += each_div
                        tail_div_list.append((ind, each_div))
                    else:
                        pass
        else:
            return


        def extract_content():
            text = ''
            if index_content_list:
                text = self._pretty_text(index_content_list)
                text = text.strip()
            return text

        def extract_pubtime():
            pubtime = ''
            tmp_top_div_list = copy.deepcopy(top_div_list)
            while tmp_top_div_list:
                ind, item = tmp_top_div_list.pop()
                if not item.strip():
                    continue
                div_selector = etree.HTML(item)
                if div_selector is None:
                    continue
                div_text = div_selector.xpath('string(.)').strip()
                if not div_text:
                    continue
                pubtime = re.search(r'(\d{4}\s*[年\-:/\.]\s*)\d{1,2}\s*[月\-：/\.]\s*\d{1,2}\s*[\-_:日\.]?\s*\d{1,2}\s*:\s*\d{1,2}\s*(:\s*\d{1,2})?', div_text, flags=re.S|re.I)
                if pubtime:
                    pubtime = pubtime.group()
                    index = ind
                    break
            if not pubtime:
                tmp_top_div_list = copy.deepcopy(top_div_list)
                while tmp_top_div_list:
                    ind, item = tmp_top_div_list.pop()
                    if not item.strip():
                        continue
                    div_selector = etree.HTML(item)
                    if div_selector is None:
                        continue
                    div_text = div_selector.xpath('string(.)')
                    pubtime = re.search(r'(\d{4}\s*[年\-:/\.]\s*)\d{1,2}\s*[月\-：/\.]\s*\d{1,2}\s*[\-_:日/\.]?', div_text, flags=re.S)
                    if pubtime:
                        pubtime = pubtime.group()
                        index = ind
                        break
            if not pubtime:
                tmp_top_div_list = copy.deepcopy(top_div_list)
                while tmp_top_div_list:
                    ind, item = tmp_top_div_list.pop()
                    if not item.strip():
                        continue
                    div_selector = etree.HTML(item)
                    if div_selector is None:
                        continue
                    div_text = div_selector.xpath('string(.)')
                    pubtime = re.search(r'(\d{2})/(\d{2})/(\d{4})\s*\d{1,2}\s*:\s*\d{1,2}\s*(:\s*\d{1,2})?', div_text, flags=re.S)
                    if pubtime:
                        tmp_pubtime = pubtime.group()
                        tmp_day, tmp_time = tmp_pubtime.split()
                        pubtime = f'{pubtime.groups()[2]}-{pubtime.groups()[0]}-{pubtime.groups()[1]} {tmp_time}'
                        index = ind
                        break
            if not pubtime:
                tmp_top_div_list = copy.deepcopy(top_div_list)
                while tmp_top_div_list:
                    ind, item = tmp_top_div_list.pop()
                    if not item.strip():
                        continue
                    div_selector = etree.HTML(item)
                    if div_selector is None:
                        continue
                    div_text = div_selector.xpath('string(.)')
                    pubtime = re.search(r'\d{2}\.\d{2}\.\d{2}', div_text, flags=re.S)
                    if pubtime:
                        pubtime = pubtime.group()
                        index = ind
                        break
                if pubtime:
                    tmp = pubtime.split('.')
                    pubtime = '{0}-{1}-{2}'.format('20'+tmp[0], tmp[1], tmp[2])
            if not pubtime:
                tmp_tail_div_list = copy.deepcopy(tail_div_list)
                while tmp_tail_div_list:
                    ind, item = tmp_tail_div_list.pop(0)
                    if not item.strip():
                        continue
                    div_selector = etree.HTML(item)
                    if div_selector is None:
                        continue
                    div_text = div_selector.xpath('string(.)')
                    pubtime = re.search(r'(\d{4}\s*[年\-:/\.]\s*)\d{1,2}\s*[月\-：/\.]\s*\d{1,2}\s*[\-_:日/\.]?', div_text, flags=re.S)
                    if pubtime:
                        pubtime = pubtime.group()
                        index = ind
                        break
            if not pubtime:
                head_content = ''
                tail_content = ''
                if index_content_list:
                    text = self._pretty_text(index_content_list)
                    text = text.strip()
                    head_content = text.split('\n')[0]
                    tail_content = text.split('\n')[-1]
                    if not pubtime:
                        pubtime = re.search(r'(\d{4}\s*[年\-:/\.]\s*)\d{1,2}\s*[月\-：/\.]\s*\d{1,2}\s*[\-_:日/\.]?', head_content, flags=re.S)
                        if pubtime:
                            pubtime = pubtime.group()
                    if not pubtime:
                        pubtime = re.search(r'(\d{4}\s*[年\-:/\.]\s*)\d{1,2}\s*[月\-：/\.]\s*\d{1,2}\s*[\-_:日/\.]?', tail_content, flags=re.S)
                        if pubtime:
                            pubtime = pubtime.group()
            if pubtime:
                pubtime = pubtime.strip()
                pubtime = pubtime.replace('年', '-').replace('月', '-').replace('日', ' ').replace('/', '-').replace('.', '-')
                pubtime = utils.drop_mutil_blank(pubtime)
                pubtime = utils.tidy_time(pubtime)
                # return pubtime, index
                return pubtime, 0
            else:
                return pubtime, 0

        def extract_title():
            title = ''
            selector = etree.HTML(top_text)
            tmps = selector.xpath('//body//h1|//body//h2|//body//h3|//body//h4')
            if not tmps:
                tmps = selector.xpath('//h1|//h2|//h3|//h4')
            tmp_title_list = list()
            title_list = list()
            for tmp in tmps:
                title_str = tmp.xpath('string(.)').strip()
                tmp_title_list.append((len(title_str), title_str))
                title_list = sorted(tmp_title_list, key=itemgetter(0))
            while title_list:
                title_str_tuple = title_list.pop()
                title_str = title_str_tuple[1]
                if nlp.is_longsent(title_str):
                    title_str = nlp.clear_pan(title_str)
                    title = utils.drop_null(title_str)
                    break
            # print('*************title1********', title)
            if not title:
                top_div_list = list()
                for ind, each_div in enumerate(re.findall("<div>(.*?)</div>", html, flags=re.S)):
                    div_str = re.sub(r"<ul\s+[^>]*?>.*?</ul>", "", each_div, flags=re.I | re.S)
                    div_str = re.sub(r"<a\s+[^>]*?>.*?</a>", "", div_str, flags=re.I | re.S)
                    if ind > index - 1:
                        break
                    if div_str.strip():
                        top_div_list.append((ind, each_div))
                tmp_top_div_list = copy.deepcopy(top_div_list)
                while tmp_top_div_list:
                    ind, item = tmp_top_div_list.pop()
                    if abs(index - ind) > 5:
                        break
                    if not item.strip():
                        continue
                    div_selector = etree.HTML(item)
                    if div_selector is None:
                        continue
                    div_text = div_selector.xpath('string(.)').strip()
                    filter_toptext = re.sub(r'[^\u4E00-\u9FFF]', '', div_text, flags=re.S).strip()
                    if len(filter_toptext) >= 6:
                        title = div_text
                        if '\n' in div_text:
                            title = div_text.split('\n')[0]
                        break
            # print('*************title2********', title)
            selector = etree.HTML(html)
            if not title:
                tmps = selector.xpath('//title/text()')
                if tmps:
                    title = tmps[0].strip()
                    title = nlp.clear_title(title)

            return title

        news = {}

        news_content = extract_content()

        news_pubtime, index = extract_pubtime()
        news_title = extract_title()
        news['news_content'] = news_content
        news['news_pubtime'] = news_pubtime
        news['news_title'] = news_title

        return news



def online_parse(url):
    parser = NewsParser()
    html = get_html(url)
    article = parser.extract_news(html)
    return article

def offline_parse(html):
    parser = NewsParser()
    article = parser.extract_news(html)
    return article


if __name__ == '__main__':
    urls = [
        # "http://news.xinhuanet.com/politics/2017-09/20/c_129708380.htm",
        # "http://society.huanqiu.com/article/2017-09/11267378.html?from=bdwz",
        # "http://news.ifeng.com/a/20170920/52088156_0.shtml?_zbs_baidu_news",
        # "https://baijia.baidu.com/s?id=1579038125281644965",
        # "https://baijia.baidu.com/s?id=1578947482988642727",
        # "http://www.gtgqw.com/showhysj142830.html",
        # "http://www.96369.net/news/429/429145.html",
        # "http://www.china5e.com/news/news-1003412-1.html",
        # "http://www.tiekuangshi.com/news/62611.htm",
        # "http://www.100ppi.com/news/detail-20170921-1127881.html",
        # "http://www.steelmart.cn/news/detailed-100101100100000163.html",
        # "http://www.steelmart.cn/news/detailed-100101100100000162.html",
        # "http://xj.people.com.cn/n2/2017/0919/c188514-30748560.html",
        # "http://www.opsteel.cn/news/2017-09/59A7F7121D44AC7AE050080A7EC911AC.html",
        # "http://xj.people.com.cn/n2/2017/0919/c188514-30748560.html",
        # "http://www.gangtie7.com/news/detail.php?id=44666",
        # "http://shidian.lgmi.com/html/201709/15/1450.htm",
        # "http://info.lgmi.com/html/201709/21/3278.htm",
        # "http://info.lgmi.com/html/201703/21/7545.htm",
        # "http://news.zgw.com/gcdt/20170921/195837.html",
        # "http://m.ce.cn/gs/gd/201709/22/t20170922_26222697.shtml"
        # 'https://baijia.baidu.com/s?id=1578947482988642727',
        # 'http://info.lgmi.com/html/201703/21/7545.htm',
        # 'http://guba.eastmoney.com/news,cjpl,732561919.html',
        # 'http://www.yicai.com/news/5378058.html',
        # 'http://www.ce.cn/cysc/ny/gdxw/201711/28/t20171128_27017151.shtml',
        # 'http://www.szse.cn/main/disclosure/bsgg_front/39775934.shtml',
        # 'http://www.coal.com.cn/News/395081.htm',
        # 'http://app.finance.china.com.cn/report/detail.php?id=4001355%27'
        # 'http://kuaixun.stcn.com/2017/1128/13796754.shtml',
        # 'http://www.zhaomei.com/news/view/10690',
        # 'http://www.zh818.com/view.aspx?id=14544905',
        # 'http://news.steelcn.cn/a/120/20171019/926149A7197523.html',
        # 'http://finance.ce.cn/jjpd/jjpdgd/201703/14/t20170314_20973709.shtml',
        # 'http://finance.ce.cn/rolling/201710/17/t20171017_26555693.shtml',
        # 'http://info.lgmi.com/html/201711/28/7380.htm',
        # 'http://www.yicai.com/news/5378058.html',
        # 'http://news.mysteel.com/17/1128/17/B0D3D9E72FC346DA.html',
        # 'http://www.cpnn.com.cn/zdyw/201804/t20180412_1064856.html',
        # 'http://www.mohurd.gov.cn/dfxx/201606/t20160613_227753.html',
        # 'http://news.newmaker.com/news_85272.html',
        # 'http://www.chemall.com.cn/chemall/infocenter/newsfile/2018-7-24/2018724145356.html'
        # 'http://wdgt.roboo.com/touch/inewsdetail.rob?rid=e0811776137b3cf348e527f59c1be426&index=nnews-business&ver=touch&cid=249038',
        # 'http://www.chemall.com.cn/chemall/infocenter/newsfile/2018-7-23/2018723113719.html',
        # 'http://www.gov.cn/zhengce/2018-07/23/content_5308504.htm',
        # 'http://njnew.6636.net/nxtcbf/toArticle?articleId=ff80808163d042710164b18d594e5db0&lanmuid=4028800c23bb81140123bb96604a002c',
        # 'http://njnew.6636.net/nxtcbf/toArticle?articleId=ff80808163d043680164c4e952b70e62&lanmuid=4028800c23bb81140123bb9700810030',
        # 'http://www.shfe.com.cn/news/news/911330884.html',
        'http://www.mohurd.gov.cn/zxydt/201801/t20180116_234827.html',
        # 'http://www.fishfirst.cn/search.php?mod=forum&searchid=403&orderby=lastpost&ascdesc=desc&searchsubmit=yes&kw=%B8%AF%D6%B2%CB%E1%C4%C6'
    ]
    for url in urls:
        print(url)
        body = online_parse(url=url)
        if not body:
            continue
        print(body)
        print(body['news_content'])
        print(body['news_pubtime'])
        print(body['news_title'])
        print('+++++++++++++++==')
