# -*- coding: UTF-8 -*-
import urllib2, re, urlparse
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson.binary import Binary
import time
import random
import os, shutil
import zlib

try:
    import cPickle as pickle        # cPickle是c语言写的，速度快
except ImportError:
    import pickle

DEFAULT_AGENT = 'Sogou spider'
DEFAULT_DELAY = 0
DEFAULT_RETRIES = 2

# 下载：获取url的html
class Downloader:
    def __init__(self, delay=DEFAULT_DELAY, user_agent=DEFAULT_AGENT, proxies=None, num_retries=DEFAULT_RETRIES, opener=None, cache=None):
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.num_retries = num_retries
        self.opener = opener
        self.cache = cache

    def __call__(self, url):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError:
                pass
            else:
                if self.num_retries > 0 and 500 <= result['code'] < 600:
                    result = None
        if result is None:
            self.throttle.wait(url)
            proxy = random.choice(self.proxies) if self.proxies else None
            result = self.download(url, self.user_agent, proxy, self.num_retries)
            if self.cache:
                self.cache[url] = result
        return result['html']

    def download(self, url, user_agent, proxy, num_retries, data=None):
        print 'Downloading:', url
        headers = {'User_agent': user_agent}
        request = urllib2.Request(url, headers=headers)

        opener = self.opener or urllib2.build_opener()
        if proxy:
            proxy_params = {urlparse.urlparse(url).scheme: proxy}
            opener.add_handler(urllib2.ProxyHandler(proxy_params))

        try:
            response = opener.open(request)
            html = response.read()
            code = response.code
        except Exception as e:
            print 'Download error:', str(e)
            html = None
            if hasattr(e, 'code'):
                code = e.code
                if num_retries > 0 and 500 <= code < 600:
                    return self.download(self, url, user_agent, proxy, num_retries-1)
            else:
                code = None
        return {'html': html, 'code': code}


# 爬取同一域名下的不同网页时，要延时，特别是在多线程爬虫中
class Throttle:
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = urlparse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()


# 磁盘缓存：缓存html
class DiskCache:
    def __init__(self, cache_dir='cache', expires=timedelta(days=30), compress=True):
        self.cache_dir = cache_dir
        self.expires = expires
        self.compress = compress

    def __getitem__(self, url):
        path = self.url_to_path(url)
        if os.path.exists(path):
            with open(path, 'rb') as fp:
                data = fp.read()                                # 读取文件，返回字符串data
                if self.compress:
                    data = zlib.decompress(data)                # 解压字符串data，返回字符串data
                result, timestamp = pickle.loads(data)          # 将字符串data读出，返回元组(result, timestamp)
                if self.has_expired(timestamp):
                    raise KeyError(url + ' has expired')
                return result
        else:
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, result):
        path = self.url_to_path(url)
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)

        data = pickle.dumps((result, datetime.utcnow()))        # 将时间戳与result组成的元组写入，返回字符串data
        if self.compress:
            data = zlib.compress(data)                          # 压缩字符串data，返回字符串data
        with open(path, 'wb') as fp:
            fp.write(data)                                      # 将字符串data写入文件

    def __delitem__(self, url):
        path = self.url_to_path(url)
        try:
            os.remove(path)
            os.removedirs(os.path.dirname(path))
        except OSError:
            pass

    def url_to_path(self, url):
        components = urlparse.urlsplit(url)
        path = components.path
        if not path:
            path = '/index.html'
        elif path.endswith('/'):
            path += 'index.html'
        elif not os.path.splitext(path)[1]:                                     # 获取后缀名，为空则加上.html
            path += '.html'
        filename = components.netloc + path + components.query
        filename = re.sub('[^/0-9a-zA-Z\-.,;_]', '_', filename)                 # 将非法字符替换为下划线
        filename = '/'.join(segment[:255] for segment in filename.split('/'))   # 限制文件名最大长度为255
        return os.path.join(self.cache_dir, filename)

    def has_expired(self, timestamp):
        return datetime.utcnow() > timestamp + self.expires

    def clear(self):
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)


# 数据库缓存——MongoDB
class MongoCache:
    def __init__(self, client=None, db_name='db_name', collect_name='collect_name', expires=timedelta(days=30)):
        self.client = MongoClient('localhost', 27017) if client is None else client             # 创建数据库
        self.db = self.client[db_name]                                                          # 定义数据库名db_name
        self.collect = self.db[collect_name]                                                    # 定义集合名collect_name，或使用方法createCollection()
        self.collect.create_index('timestamp', expireAfterSeconds=expires.total_seconds())      # 创建timestamp索引，到期MongoDB自动删除

    def __contains__(self, url):
        try:
            self[url]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, url):
        record = self.collect.find_one({'_id': url})                                            # 取出record ———— find_one()：找出符合条件的第一条记录
        if record:
            result = record['result']
            return pickle.loads(zlib.decompress(result))
        else:
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, result):
        result = Binary(zlib.compress(pickle.dumps(result)))                                    # 注意这里将压缩后的字符串使用了Binary()
        record = {'result': result, 'timestamp': datetime.utcnow()}
        self.collect.update({'_id': url}, {'$set': record}, upsert=True)                        # 插入或更新record ———— update()：无返回值

    def clear(self):
        self.collect.drop()
