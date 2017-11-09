# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re, itertools
import lxml.html
import csv, codecs

from link_crawler import download, Throttle, get_robots


def page_crawler(seed_url, delay=0, max_depth=-1, max_urls=-1, user_agent='Sogou spider', scrape_callback=None):

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
            if num_urls-1 == max_urls:
                break
        else:
            print 'Blocked by robots.txt:', url
    print '抓取的链接数：' + str(num_urls-1)
    return num_urls-1

def pages_crawler(seed_url, scrape_callback=None):
    url_part = ['https://nj.lianjia.com/ershoufang/qilinzhen/pg', 'l2a2p4']
    total_crawler = 0
    total_num = get_totalnum(seed_url)

    for i in itertools.count(1):
        pages = str(i).join(url_part)
        num = page_crawler(pages, scrape_callback=scrape_callback)
        total_crawler += num
        if total_crawler == total_num:
            break

def get_totalnum(url):
    html = download(url)
    tree = lxml.html.fromstring(html)
    totalnum = tree.cssselect('div.resultDes.clear > h2.total.fl > span')[0].text_content()
    return int(totalnum)

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
        file_obj = open(filename, 'wb')
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
    scrape_callback = ScrapeCallback(filename, fields)

    url = 'https://nj.lianjia.com/ershoufang/qilinzhen/l2a2p4'
    pages_crawler(url, scrape_callback)
