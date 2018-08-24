# coding:utf-8

from lxml import etree
import re
import copy

from handle_html import strip_tag
from handle_html import HtmlHandle


class ExtractTable(object):

    def __init__(self):
        self.col_num = 2
        self.row_num = 2

    @staticmethod
    def get_empty_col(line_lst):
        tail_index = 0
        for ix, item in enumerate(line_lst):
            if item == 'null':
                tail_index = ix
                break
        return tail_index

    def tidy_table(self, selector):
        table = [['null' for _ in range(20)] for _ in range(10000)]
        for tr_index, tr in enumerate(selector.xpath('.//tr')):
            # 处理表格的行与列
            for td_index, td in enumerate(tr.xpath('.//td|th')):
                row_span = int(td.xpath('./@rowspan')[0]) if td.xpath('./@rowspan') else 1  # int
                col_span = int(td.xpath('./@colspan')[0]) if td.xpath('./@colspan') else 1  # int
                cell_content = td.xpath('string(.)').strip()
                # print(row_span, col_span, cell_content)
                for col_i in range(col_span):
                    # 判断当前行中第几列为空
                    # print('***',tr_index)
                    cur_col = self.get_empty_col(table[tr_index])
                    for row_i in range(row_span):
                        cur_row = tr_index + row_i
                        table[cur_row][cur_col] = cell_content
        html = []
        for row in table:
            col_lst = []
            if row[0] == 'null':
                break
            for col in row:
                if col == 'null':
                    break
                row_str = f'<td>{col}</td>'
                col_lst.append(row_str)
            html.append('\n'.join(col_lst))
        html = '\n</tr>\n<tr>\n'.join(html)
        html = f'<tr>\n{html}\n</tr>'
        return etree.HTML(html)

    def find_table(self, html):
        """定位表格"""
        # 去除噪声标签
        handle_html = HtmlHandle.handle_html(html_str=html)
        html = strip_tag(handle_html)
        # 抽取表格
        tab_selector_lst = []
        selector = etree.HTML(html)
        count = len(selector.xpath('//table'))
        for ix in range(count):
            sub_selectors = selector.xpath(f'//table[position()={ix+1}]')
            if len(sub_selectors) == 1:
                sub_selector = sub_selectors[0]
                sub_selector = self.tidy_table(sub_selector)
                # 抽取表格标题
                title = ''
                pre_nodes = selector.xpath(f'//table[position()={ix+1}]/preceding-sibling::*')
                while pre_nodes:
                    pre_node = pre_nodes.pop()
                    node_str = pre_node.xpath('string(.)').strip()
                    node_str = node_str.replace(' ', '').replace('\n', '')
                    title = node_str
                    if node_str:
                        break
                tab_selector_lst.append(
                    {
                        'title': title,
                        'selector': sub_selector
                    }
                )
        return tab_selector_lst

    def split_table(self, selector):
        """返回分割表格后的起始位置"""
        if selector is None:
            return
        lst = []
        pos_lst = []
        for tr in selector.xpath('.//tr'):
            m = len({item.xpath('string(.)') for item in tr.xpath('./td|th')})
            tr_len = len(tr.xpath('.//td|th')) if tr.xpath('.//td|th') else 0
            tr_len = tr_len if m != 1 else 1
            lst.append(tr_len)
        tmp_lst = []
        lst.append(-1)
        start = 0
        end = 0
        found_table = False
        in_table = False
        for index in range(len(lst) - 1):
            if lst[index + 1] == lst[index]:
                in_table = True
            if found_table is False and in_table is True:
                found_table = True
                start = index
            if found_table is True and in_table is False:
                end = index
                tmp_lst.append((start, end))
                found_table = False
            in_table = False
        # 过滤3行3列以下的
        for st, ed in tmp_lst:
            if (ed - st) >= 1 and lst[ed] > 1:
                pos_lst.append((st, ed))
        return pos_lst

    def parse_table(self, selector, st, ed):
        """通过起始位置解析表格对象"""
        body = []
        title = ''
        for tr in selector.xpath(f'.//tr[position()>{st} and position()<= {ed+1}]'):
            tr_lst = []
            for td in tr.xpath('.//td|th'):
                tr_lst.append(td.xpath('string(.)').strip())
            body.append(tr_lst)
        title_tmp = selector.xpath(f'.//tr[position()={st+1}]')
        if title_tmp:
            title_tmp = title_tmp[0].xpath('preceding-sibling::tr')
            if title_tmp:
                try:
                    title = title_tmp[-1].xpath('./td')[0]
                    title = title.xpath('string(.)').strip()
                except Exception as e:
                    pass
        return title, body

    def extract_table(self, html, xpath_path=''):
        tables = []
        if xpath_path:
            dom_tree = etree.HTML(html)
            selectors = dom_tree.xpath(xpath_path)
            print(selectors[0].xpath('string(.)'))
            table_lst = [{'title': '', 'selector': selector} for selector in selectors]
        else:
            table_lst = self.find_table(html)
        for item in table_lst:
            title = item.get('title')
            selector = item.get('selector')
            for st, ed in self.split_table(selector):
                bak, body = self.parse_table(selector, st, ed)
                if bak:
                    title = bak
                if body:
                    tables.append(
                        {
                            'title': title,
                            'body': body
                        }
                    )
        print(tables)
        return tables



if __name__ == '__main__':
    url = 'http://info.10010.com/database/roaming/page.html'
    url = 'http://www.w3school.com.cn/xpath/xpath_syntax.asp'
    # url = 'http://www.czce.com.cn/cn/jysj/ccpm/H770304index_1.htm'
    # url = 'http://www.czce.com.cn/cn/DFSStaticFiles/Future/2018/20180823/FutureDataHolding.htm'
    html = HtmlHandle.handle_html(url)
    strip_html = strip_tag(html)
    e = ExtractTable()
    e.extract_table(strip_html)




