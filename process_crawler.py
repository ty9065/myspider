# -*- coding: UTF-8 -*-
import re, urlparse, robotparser
import time, threading, multiprocessing, os
import lxml.html
import csv
from pymongo import errors
from classes import Downloader, MongoCache
from MongoQueue import MongoQueue


SLEEP_TIME = 1
num_urls = 0

def threaded_crawler(seed_url, link_regex=None, delay=5, max_depth=1, max_urls=-1, user_agent = 'Sogou spider',\
                 proxies=None, num_retries=2, scrape_callback=None, cache=None, crawl_queue=None, max_threads=2):

    rp = get_robots(seed_url)
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, cache=cache)

    def process_queue():                                            # 将函数中的循环定义成方法，作线程用
        global num_urls                                             # 内层函数修改num_urls的值，不使用global会报错
        while crawl_queue:
            try:
                url = crawl_queue.pop()
            except KeyError:
                break

            if rp.can_fetch(user_agent, url):
                html = D(url)

                if scrape_callback:
                    scrape_callback(url, html)

                if crawl_queue.get_depth(url) != max_depth:
                    for link in get_links(html):
                        if re.match(link_regex, link):
                            link = urlparse.urljoin(seed_url, link)
                            try:
                                crawl_queue.push(link)
                                crawl_queue.update_depth(link)
                            except errors.DuplicateKeyError:
                                pass
                crawl_queue.complete(url)

                num_urls += 1
                print '进程{}-->抓取的链接数：{}'.format(os.getpid(), str(num_urls))
                if max_urls == crawl_queue.db.crawl_queue.find().count():
                    break
            else:
                print 'Blocked by robots.txt:', url

    threads = []
    while threads or crawl_queue:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue.peek():
            thread = threading.Thread(target=process_queue)         # 创建线程
            thread.setDaemon(True)                                  # 设置此线程被主线程守护回收。默认False不回收，需要在 start 方法前调用
            thread.start()
            threads.append(thread)

        time.sleep(SLEEP_TIME)

    print '抓取的总链接数：' + str(crawl_queue.db.crawl_queue.find().count())

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

def process_link_crawler(args, **kwargs):                                                   # 传入多个参数
    num_cpus = multiprocessing.cpu_count()
    print 'Staring {} processes'.format(num_cpus)
    processes = []
    for i in range(num_cpus):
        p = multiprocessing.Process(target=threaded_crawler, args=[args], kwargs=kwargs)    # 创建进程，注意参数写法
        p.start()       # 启动子进程
        processes.append(p)
    for p in processes:
        p.join()        # 使子进程运行结束后再执行父进程

if __name__ == '__main__':
    url = 'http://example.webscraping.com'
    link_regex = '/(places/default/index|places/default/view)'
    cache = MongoCache()
    cache.clear()                           # 缓存解析过的url，可以不清空
    crawl_queue = MongoQueue()
    crawl_queue.clear()                     # 缓存队列一定要清空
    crawl_queue.push(url)
    process_link_crawler(url, link_regex=link_regex, cache=cache, crawl_queue=crawl_queue)

