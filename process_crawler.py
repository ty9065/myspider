# -*- coding: UTF-8 -*-
import re, urlparse, robotparser
import time, threading, multiprocessing, os
import lxml.html
import csv, codecs
from pymongo import errors
from classes import Downloader, MongoCache
from MongoQueue import MongoQueue

DEFAULT_AGENT = 'Sogou spider'  # 代理
DEFAULT_DELAY = 5               # 延时
DEFAULT_RETRIES = 2             # 重试次数
DEFAULT_MAX_DEPTH = 2           # 最大深度，不想限制可设置为-1
DEFAULT_MAX_URLS = 25           # 最大url数，不想限制可设置为-1（注意：多进程时该功能不完善，设置为-1时要改成==）
DEFAULT_MAX_THREADS = 2         # 最大线程数
SLEEP_TIME = 1                  # 线程延时
num_urls = 0                    # 全局变量，用来观察各进程抓取的链接数，便于理解进程
                                # 可发现各进程为独立的内存，不能相互访问，各自维护全局变量

def func_process(seed_url, link_regex=None, fields=None, cache=None, crawl_queue=None, datas=None,\
                 delay=DEFAULT_DELAY, user_agent = DEFAULT_AGENT, proxies=None, num_retries=DEFAULT_RETRIES,\
                 max_depth=DEFAULT_MAX_DEPTH, max_urls=DEFAULT_MAX_URLS, max_threads=DEFAULT_MAX_THREADS):

    rp = get_robots(seed_url)
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, cache=cache)

    def process_queue():                                            # 将函数中的循环定义成方法，作线程用
        global num_urls                                             # 内层函数修改num_urls的值，不使用global会报错
        while True:
            try:
                url = crawl_queue.pop()                             # 找出状态为outstanding的记录，并置为processing
            except KeyError:                                        # 否则，调用repair()，并抛出异常
                break

            if rp.can_fetch(user_agent, url):
                html = D(url)
                crawl_queue.complete(url)                           # 状态置为complete，下载好之后就置为complete状态比较妥当
                                                                    # 以免后文出现break使得状态无法更改，从而导致不必要的超时处理
                if fields:
                    get_datas(datas, url, html, fields)                     # 多进程存到数据库
                    # print datas.collect.find().count()
                    # if max_urls <= datas.collect.find().count():          # 统计数据总数时，判断代码放在这儿
                    #     break

                print cache.collect.find().count()                  # 用来观察多进程下不是线性增加
                if max_urls <= cache.collect.find().count():        # 统计链接总数（注意：多进程时不是线性增加，需改==为<=）
                    break                                           # break要放在queue_add()之前，否则多进程下max_url限制不住

                if crawl_queue.get_depth(url) != max_depth:
                    queue_add(crawl_queue, html, link_regex, seed_url)      # 调用函数更新crawl_queue

                num_urls += 1
                print '进程{}-->抓取的链接数：{}'.format(os.getpid(), str(num_urls))

            else:
                print 'Blocked by robots.txt:', url

    multi_thread(func_thread=process_queue, crawl_queue=crawl_queue, max_threads=max_threads)       # 调用多线程函数处理crawl_queue

def queue_add(crawl_queue, html, link_regex, seed_url):
    for link in get_links(html):
        if re.match(link_regex, link):
            link = urlparse.urljoin(seed_url, link)
            try:
                crawl_queue.push(link)                              # 状态置为outstanding
                crawl_queue.update_depth(link)                      # 插入新数据则depth+1，重复则不处理
            except errors.DuplicateKeyError:
                pass

def get_links(html):
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)

def get_datas(datas, url, html, fields):
    if re.search('/view/', url):
        tree = lxml.html.fromstring(html)
        row = [url]
        for field in fields[1:]:
            row.append(tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content())
        datas[url] = row                                # 调用__setitem__方法，写入数据库

def get_robots(url):
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp


class file_save:
    def __init__(self, filename, fields):
        self.filename = filename
        self.fields = fields
        file_obj = open(self.filename, 'wb')
        file_obj.write(codecs.BOM_UTF8)  # 防止乱码
        self.writer = csv.writer(file_obj)
        self.writer.writerow(self.fields)

    def write_file(self, datas):
            for data in datas.collect.find():
                url = data['_id']
                self.writer.writerow(datas[url])        # 调用__getitem__方法，从数据库取出，并写入文件
            print '文件{}写入完成！'.format(self.filename)


def multi_thread(func_thread=None, crawl_queue=None, max_threads=None):
    threads = []
    while threads or crawl_queue:                                   # 调用__nonzero__方法：状态不是complete则为True
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue.peek():    # 判断是否还有outstanding的记录
            thread = threading.Thread(target=func_thread)           # 创建线程
            thread.setDaemon(True)                                  # 设置此线程被主线程守护回收。默认False不回收，需要在start方法前调用
            thread.start()
            threads.append(thread)
        time.sleep(SLEEP_TIME)

def multi_process(args, **kwargs):                                                      # 传入多个参数
    num_cpus = multiprocessing.cpu_count()
    print 'Staring {} processes'.format(num_cpus)
    processes = []
    for i in range(num_cpus):
        p = multiprocessing.Process(target=func_process, args=[args], kwargs=kwargs)    # 创建进程，注意参数写法
        p.start()       # 启动子进程
        processes.append(p)
    for p in processes:
        p.join()        # 使子进程运行结束后再执行父进程

def main():
    try:
        url = 'http://example.webscraping.com'
        link_regex = '/(places/default/index|places/default/view)'
        filename = 'countries.csv'
        fields = ('url', 'area', 'population', 'iso', 'country', 'capital',
                  'continent', 'tld', 'currency_code', 'currency_name',
                  'phone', 'postal_code_format', 'postal_code_regex',
                  'languages', 'neighbours')

        webpage = MongoCache(db_name='cache', collect_name='webpage')
        crawl_queue = MongoQueue(db_name='cache', collect_name='crawl_queue')
        datas = MongoCache(db_name='cache', collect_name='datas')

        webpage.clear()                         # 缓存解析过的url，可以不清空
        crawl_queue.clear()                     # 缓存队列一定要清空
        datas.clear()                           # 缓存要写入文件的数据，可以不清空

        crawl_queue.push(url)
        multi_process(url, link_regex=link_regex, fields=fields, cache=webpage, crawl_queue=crawl_queue, datas=datas)
    except:
        pass
    finally:                                    # 保证中途暂停程序也可以写入文件
        print '抓取的总链接数：{}'.format(webpage.collect.find().count())
        print '抓取的总数据数：{}'.format(datas.collect.find().count())
        datainfo = file_save(filename, fields)
        datainfo.write_file(datas)              # 单进程写入文件

if __name__ == '__main__':
    main()
