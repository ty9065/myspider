# -*- coding: UTF-8 -*-
import urllib2, re, urlparse, robotparser
import datetime, time
import lxml.html
import csv
from classes import Downloader, DiskCache

def download(url, user_agent='Sogou spider', proxy=None, num_retries=2):
    print 'Downloading:', url
    headers = {'User_agent': user_agent}
    request = urllib2.Request(url, headers=headers)

    opener = urllib2.build_opener()
    if proxy:
        proxy_params = {urlparse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_params))

    try:
        html = opener.open(request).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url, user_agent, proxy, num_retries-1)
    return html

def link_crawler(seed_url, link_regex=None, delay=0, max_depth=1, max_urls=-1, user_agent = 'Sogou spider',\
                 proxies=None, num_retries=2, scrape_callback=None, cache=None):

    crawl_queue = [seed_url]
    seen = {seed_url: 0}
    num_urls = 0

    rp = get_robots(seed_url)
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, cache=cache)

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
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print 'Blocked by robots.txt:', url
    print '抓取的链接数：' + str(num_urls)

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
    # download('http://httpstat.us/500')
    link_crawler('http://example.webscraping.com', '/(places/default/index|places/default/view)', cache=DiskCache())


