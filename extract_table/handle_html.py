# coding:utf-8

import urllib
from urllib.parse import urlparse
from html.parser import HTMLParser


from bs4 import BeautifulSoup
import chardet
from fake_useragent import UserAgent
from tidylib import Tidy



class HtmlHandle(object):

    @staticmethod
    def fetch_html(url):
        """获取网页的html源码"""
        ua = UserAgent()
        url_parse = urlparse(url)
        headers = {
            "User-Agent": ua.random,
            "Referer": "{}://{}".format(url_parse.scheme, url_parse.netloc),
        }
        req = urllib.request.Request(url=url, headers=headers)
        try:
            res = urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            print(e)
            return ''
        text = res.read()
        code_detect = chardet.detect(text)['encoding']
        if code_detect:
            html_str = text.decode(code_detect, 'ignore')
        else:
            html_str = text.decode("utf-8", 'ignore')
        return html_str

    @staticmethod
    def pretty_html(html_str):
        """格式化html源代码"""
        soup = BeautifulSoup(html_str, 'html.parser')
        soup_html = soup.prettify()
        return soup_html

    @staticmethod
    def tidy_html(html_str):
        """补齐html缺失标签"""
        tidy = Tidy()
        tidy_html, errors = tidy.tidy_document(html_str)
        return tidy_html

    @classmethod
    def handle_html(cls, url='', html_str=''):
        """处理html代码包括采集网页/格式化/补齐代码"""
        if html_str:
            tidy_html = cls.tidy_html(html_str)
            soup_html = cls.pretty_html(tidy_html)
            return soup_html
        elif url:
            html_str = cls.fetch_html(url)
            tidy_html = cls.tidy_html(html_str)
            soup_html = cls.pretty_html(tidy_html)
            return soup_html
        else:
            raise Exception(f'url, html_str 参数缺失')


class StripParser(HTMLParser):
    """去除一些特定的标签"""
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.drop_tags = {'script', 'style', 'iframe', 'aside', 'nav', 'footer'}
        self.fed = []
        self.point_tags =[]
        self.is_fed = True

    def handle_starttag(self, tag, attrs):
        if tag in self.drop_tags:
            self.is_fed = False
            self.point_tags.append(tag)
        else:
            if tag in {'table', 'div'}:
                self.fed.append('<table>')
            else:
                tmp_attrs = ['{0}="{1}"'.format(i[0], i[1]) for i in attrs]
                tmp_attrs = ' '.join(tmp_attrs)
                self.fed.append('<{} {}>'.format(tag, tmp_attrs))

    def handle_data(self, data):
        if self.is_fed:
            self.fed.append(data)

    def handle_endtag(self, tag):
        if tag in self.drop_tags:
            if tag == self.point_tags[-1]:
                self.point_tags.pop()
            if not self.point_tags:
                self.is_fed = True
        else:
            if tag == 'div':
                self.fed.append('</table>')
            else:
                self.fed.append('</{}>'.format(tag))

    def get_html(self):
        return '\n'.join(self.fed)

    @classmethod
    def strip_tag(cls, html):
        return cls.feed(html)


def strip_tag(html):
    """
    去除html特定的标签
    :param html: string
    :return: string
    """
    s = StripParser()
    s.feed(html)
    return s.get_html()



if __name__ == '__main__':
    html = HtmlHandle.handle_html('http://info.10010.com/database/roaming/page.html')
    strip_html = strip_tag(html)
    print(strip_html)
