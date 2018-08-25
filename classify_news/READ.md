#### 0.获取语料
1. 获取500个导航页的的9.2万个链接

#### 1.确定URL特征项

1. 是否含有时间项
2. 是否以'/'结尾
3. 协议是否是http/https
4. 文件类型 'jpg', 'png', 'gif', 'pdf', 'txt', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'action', 'zip', 'mp3', 'mp4'
5. 'newslist', 'user', 'login', 'logout', 'beian', 'register', 'iframe', 'account'
6. 'bbs', 'video', 'tv', 'photo', 'help', 'member', 'about', 'vblog', 'flash', 'imgs', 'img'
7. 路径长度
8. 'home', 'index'
9. 文件名的长度
10. 文件名英文字符的个数
11. 文件名数字字符的个数
12. 是否含有查询项
13. 判断链接最后是否是主域名后缀
14. 数字层级目录的个数
15. 文件名中‘-’的个数
16. 二级域名词： list\d*, index, home
17. 查询项的个数



#### 2.模型选择
    url = 'http://news.luosi.com/news-2.html'
    url = 'http://news.luosi.com/articles-11205.html'