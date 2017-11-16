# -*- coding: UTF-8 -*-
import re, urlparse, robotparser
import time, threading
import lxml.html
import csv
from classes import Downloader, MongoCache

SLEEP_TIME = 1
num_urls = 0

def threaded_crawler(seed_url, link_regex=None, delay=5, max_depth=1, max_urls=-1, user_agent = 'Sogou spider',\
                 proxies=None, num_retries=2, scrape_callback=None, cache=None, max_threads=10):

    crawl_queue = [seed_url]
    seen = {seed_url: 0}

    rp = get_robots(seed_url)
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, cache=cache)

    def process_queue():                                            # 将函数中的循环定义成方法，作线程用
        global num_urls                                             # 内层函数修改num_urls的值，不使用global会报错
        while crawl_queue:
            url = crawl_queue.pop()

            if rp.can_fetch(user_agent, url):
                html = D(url)

                if scrape_callback:
                    scrape_callback(url, html)

                depth = seen[url]
                if depth != max_depth:
                    for link in get_links(html):
                        if re.match(link_regex, link):
                            link = urlparse.urljoin(seed_url, link)
                            if link not in seen:
                                seen[link] = depth + 1
                                crawl_queue.append(link)
                num_urls += 1                                       # num_urls其实可以通过len(seen)得到
                if num_urls == max_urls:
                    break
            else:
                print 'Blocked by robots.txt:', url
        print '抓取的链接数：' + str(num_urls)

    threads = []
    while threads or crawl_queue:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue:
            thread = threading.Thread(target=process_queue)         # 创建线程
            thread.setDaemon(True)                                  # 设置此线程被主线程守护回收。默认False不回收，需要在 start 方法前调用
            thread.start()
            threads.append(thread)

        time.sleep(SLEEP_TIME)

def get_links(html):
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)

def get_robots(url):
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp


class ScrapeCallback:
    def __init__(self):
        self.writer = csv.writer(open('countries.csv', 'w'))
        self.fields = ('area', 'population', 'iso', 'country', 'capital',
                        'continent', 'tld', 'currency_code', 'currency_name',
                        'phone', 'postal_code_format', 'postal_code_regex',
                        'languages', 'neighbours')
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        if re.search('/view/', url):
            tree = lxml.html.fromstring(html)
            row = []
            for field in self.fields:
                row.append(tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content())
            self.writer.writerow(row)

if __name__ == '__main__':
    url = 'http://example.webscraping.com'
    link_regex = '/(places/default/index|places/default/view)'
    threaded_crawler(url, link_regex=link_regex, scrape_callback=ScrapeCallback(), cache=MongoCache())

