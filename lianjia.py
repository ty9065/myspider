# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re, itertools, urlparse
import lxml.html
import csv, codecs

from link_crawler import download, Throttle, get_robots


def link_crawler(seed_url, link_regex=None, delay=0, max_depth=-1, max_urls=-1, user_agent='Sogou spider', scrape_callback=None):

    crawl_queue = [seed_url]
    seen = {seed_url: 0}
    num_urls = 0

    rp = get_robots(seed_url)
    throttle = Throttle(delay)

    while crawl_queue:
        url = crawl_queue.pop()

        if rp.can_fetch(user_agent, url):
            throttle.wait(url)
            html = download(url)

            if scrape_callback:
                scrape_callback.call_lianjia(url, html)

            depth = seen[url]
            if depth != max_depth:
                for link in get_links(html):
                    if link not in seen:
                        seen[link] = depth + 1
                        crawl_queue.append(link)
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print 'Blocked by robots.txt:', url
    print '抓取的链接数：' + str(num_urls-1)

def get_pages(html):
    tree = lxml.html.fromstring(html)
    pages = []
    for i in itertools.count(0):
        try:
            page = tree.cssselect('div.page-box.house-lst-page-box > a')[i].get('href')
            pages.append(page)
        except:
            print 'error'
            break
    return pages

def get_links(html):
    tree = lxml.html.fromstring(html)
    links = []
    for i in itertools.count(0):
        try:
            link = tree.cssselect('ul.sellListContent > li.clear > a.img')[i].get('href')
            links.append(link)
        except:
            break
    links.reverse()
    return links

class ScrapeCallback:
    def __init__(self, filename, fields):
        file_obj = open(filename, 'a+')
        file_obj.write(codecs.BOM_UTF8)  # 防止乱码
        self.writer = csv.writer(file_obj)
        self.fields = fields
        self.writer.writerow(self.fields)

    def call_lianjia(self, url, html):
        if re.search('[0-9]{12}', url):
            tree = lxml.html.fromstring(html)
            row = [url]
            for field in self.fields[1:3]:
                row.append(tree.cssselect('span.{}'.format(field))[0].text_content())
            for field in self.fields[3:6]:
                row.append(tree.cssselect('div.{} > div.mainInfo'.format(field))[0].text_content())
            self.writer.writerow(row)

if __name__ == '__main__':
    filename = 'lianjia.csv'
    fields = ('url', 'total', 'unitPriceValue', 'room', 'type', 'area')
    url = ['https://nj.lianjia.com/ershoufang/qilinzhen/pg', 'l2a2p4']
    for i in range(1,7):
        result = str(i).join(url)
        link_crawler(result, scrape_callback=ScrapeCallback(filename, fields))