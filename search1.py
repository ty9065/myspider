# -*- coding: UTF-8 -*-
import json, csv
from classes import Downloader


def main():
    url = 'http://example.webscraping.com/places/ajax/' \
                   'search.json?&search_term=.&page_size=260&page=0'    # 'search_term=.'：匹配所有字符(a-z)

    writer = csv.writer(open('search1.csv', 'w'))

    D = Downloader()
    html = D(url)
    ajax = json.loads(html)                         # 作用：'str'-->'dict'
    for record in ajax['records']:
        writer.writerow([record['country']])        # [record['country']]：用[]括起来变字符串为列表，避免写入文件为单个字符

    print ajax['num_pages']                         # 将page_size设为260后，num_pages=1，即所有链接都显示在一个页面

if __name__ == '__main__':
    main()
