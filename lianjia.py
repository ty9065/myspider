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

            if re.search('[0-9]{12}', url):
                if scrape_callback:
                    scrape_callback.call_lianjia(url, html)
                num_urls += 1
                if num_urls == max_urls:
                    break

            depth = seen[url]
            if depth != max_depth:
                for link in get_links(html):
                    if link not in seen:
                        seen[link] = depth + 1
                        crawl_queue.append(link)
        else:
            print 'Blocked by robots.txt:', url
    print '抓取的链接数：' + str(num_urls)
    return num_urls

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

def link_crawler(seed_url, delay=0, max_depth=-1, max_urls=-1, page_num=1, user_agent='Sogou spider', scrape_callback=None):

    crawl_queue = [seed_url]
    seen = {seed_url: 0}
    num_urls = 0

    links = get_pages(page_num)                 # 获取page的url
                                                # links的主要作用：完成多页抓取功能，又不造成多余的循环判断
    rp = get_robots(seed_url)
    throttle = Throttle(delay)

    while crawl_queue:
        url = crawl_queue.pop()

        if rp.can_fetch(user_agent, url):
            throttle.wait(url)
            html = download(url)

            if re.search('[0-9]{12}', url):     # 只统计符合条件的链接，并写入文件
                if scrape_callback:
                    scrape_callback.call_lianjia(url, html)
                num_urls += 1
                if num_urls == max_urls:
                    break

            depth = seen[url]
            if depth != max_depth:
                links.extend(get_links(html))   # 获取要抓取的url，并扩展
                for link in links:
                    if link not in seen:
                        seen[link] = depth + 1
                        crawl_queue.append(link)
                links = []                      # for循环完成后已存入队列，需清空links，否则会扩展得越来越长，避免冗余判断
        else:
            print 'Blocked by robots.txt:', url
    print '抓取的链接数：' + str(num_urls)

def get_totalnum(url):
    html = download(url)
    tree = lxml.html.fromstring(html)
    totalnum = tree.cssselect('div.resultDes.clear > h2.total.fl > span')[0].text_content()
    return int(totalnum)

def get_pages(page_num):
    url_part = ['https://nj.lianjia.com/ershoufang/qilinzhen/pg', 'l2a2p4']
    pages = []
    for i in range(2, page_num+1):
        pages.append(str(i).join(url_part))
    pages.reverse()
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
    def __init__(self, filename, fields, title):
        file_obj = open(filename, 'wb')
        file_obj.write(codecs.BOM_UTF8)  # 防止乱码
        self.writer = csv.writer(file_obj)
        self.fields = fields
        self.title = title
        self.writer.writerow(self.title)

    def call_lianjia(self, url, html):
        tree = lxml.html.fromstring(html)
        row = [url]
        row.append(tree.cssselect('h1.main')[0].get('title'))

        for field in self.fields[0]:
            row.append(tree.cssselect('span.{}'.format(field))[0].text_content())

        row.append(tree.cssselect('span.taxtext > span')[0].text_content())

        for field in self.fields[1]:
            row.append(tree.cssselect('div.{} > div.mainInfo'.format(field))[0].text_content())
            row.append(tree.cssselect('div.{} > div.subInfo'.format(field))[0].text_content())

        row.append(tree.cssselect('div.communityName > a.info')[0].text_content())
        row.append(tree.cssselect('div.areaName > span.info')[0].text_content())

        # 有规律的数据还可以这样抓
        # for i in itertools.count(0):
        #     try:
        #         row.append(tree.cssselect('div.base > div.content > ul > li')[i].text_content())
        #     except:
        #         break

        self.writer.writerow(row)

if __name__ == '__main__':
    filename = 'lianjia.csv'
    fields = (['total', 'unitPriceValue'], ['room', 'type', 'area'])
    title = ('链接', '标题', '总价/万', '单价', '首付', '户型', '楼层', '朝向', '装修情况', '面积', '建筑类型', '小区名称', '所在区域')
    scrape_callback = ScrapeCallback(filename, fields, title)

    url = 'https://nj.lianjia.com/ershoufang/qilinzhen/l2a2p4'
    MIN_NUM = 1
    MAX_NUM = get_totalnum(url)

    # pages_crawler(url, scrape_callback=scrape_callback)     # 抓多页
    # page_crawler(url, scrape_callback=scrape_callback)      # 抓单页
    # link_crawler(url, page_num=MIN_NUM, scrape_callback=scrape_callback)                    # 抓单页
    link_crawler(url, max_urls=MAX_NUM, page_num=MAX_NUM, scrape_callback=scrape_callback)  # 抓多页
