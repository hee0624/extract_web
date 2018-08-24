## 抽取网页信息

>作者: 陈贺

>email: hee0624@163.com

&nbsp;&nbsp;web上的数据有多种多样，有结构化的表格数据，有非结构化的文本数据，有半结构化的网页数据，其中这些数据尤其重要。如何重要，我就不巴拉巴拉说了。如何提取这些表格，资讯数据成为现在急需要解决的问题。本项目案尝试解决这个问题，将该问体分成3个部分，**分类资讯页**,**抽取资讯**,**抽取表格**。下面具体介绍这三部分的实现流程。

#### 识别资讯链接
&nbsp;&nbsp;如果爬取大量的资讯，关键问题是如何识别该网页是否是资讯链接还是非资讯链接，本方案基于机器学习的方式识别资讯链接，具体流程如下：
1. 获取语料
    - 获取500个导航页的的9.2万个链接
2. 构建URL特征
    - 是否含有时间项
    - 是否以'/'结尾
    - 协议是否是http/https
    - 文件类型 'jpg', 'png', 'gif', 'pdf', 'txt', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'action', 'zip', 'mp3', 'mp4'
    - 'newslist', 'user', 'login', 'logout', 'beian', 'register', 'iframe', 'account'
    - 'bbs', 'video', 'tv', 'photo', 'help', 'member', 'about', 'vblog', 'flash', 'imgs', 'img'
    - 路径长度
    - 'home', 'index'
    - 文件名的长度
    - 文件名英文字符的个数
    - 文件名数字字符的个数
    - 是否含有查询项
    - 判断链接最后是否是主域名后缀
    - 数字层级目录的个数
    -. 文件名中‘-’的个数
    - 二级域名词： list\d*, index, home
    - 查询项的个数
3. 模型选择
 - svm 98.6%
 - 决策树 98.9%
 - 随机森林 99.1%

&nbsp;&nbsp; 该模型已经训练完成，具体使用方法
#### 抽取正文内容
1. 获取网页HTＭＬ源代码
2. 对目标新闻网页源代码进行线性重构
3. 对线性重构后的源代码惊喜去噪处理
4. 划分原始数据集
5. 聚类正文段落
6. 吸收伪噪声段落
7. 生成正文脉络段落


#### 提取表格信息
1. 定位表格
2. 切分表格
3. 解析表格



```shell
├── classify_news
│   ├── 20180805-data1.xls
│   ├── classify_news.py
│   ├── comcode.py
│   ├── domain.py
│   ├── fetch_corpus.py
│   ├── __init__.py
│   ├── model.py
│   ├── models
│   │   ├── random_forest_model.m
│   │   ├── svm_model.m
│   │   └── tree_model.m
│   ├── process_feature.py
│   └── READ.md
├── extract_news
│   ├── extract_news.py
│   ├── get_html.py
│   ├── handle_html.py
│   ├── __init__.py
│   ├── nlp.py
│   └── utils.py
├── extract_table
│   ├── extract_table.py
│   ├── handle_html.py
│   └── __init__.py
└── README.md

```