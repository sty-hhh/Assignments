import requests
import lxml
from bs4 import BeautifulSoup
from xlwt import *
import jieba

workbook = Workbook(encoding = 'utf-8')
table = workbook.add_sheet('data')
# 添加列名
table.write(0, 0, 'URL')
table.write(0, 1, 'Title')
table.write(0, 2, 'content')

# 爬取title和content
url = "https://news.ifeng.com/c/89TNORdIths"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}
f = requests.get(url, headers = headers)
soup = BeautifulSoup(f.content, 'lxml')
title = soup.find('div', {'class': 'caption-3nDTQcf1'}).find('h1', {'class': 'topic-2Eq5D0Zm'})
contents = soup.find('div', {'class': 'text-3w2e3DBc'}).find_all('p')

# 对title分词
title_list = jieba.cut(title.string.strip(), cut_all=False)
title_out = "/" .join(title_list)

article = ""
for content in contents:
    article += content.string.strip()

# 对article分词
words = jieba.cut(article, cut_all=False)
article = "/" .join(words)

# 写入文件
table.write(1, 0, url)
table.write(1, 1, title_out)
table.write(1, 2, article)

# 保存到excel
workbook.save('result.xls')