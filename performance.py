# -*- coding: UTF-8 -*-
from link_crawler import download
import re
from bs4 import BeautifulSoup
import lxml.html
import time


html = download('http://example.webscraping.com/places/default/view/239')
print re.findall('<td class="w2p_fw">(.*?)</td>', html)[1]
print re.findall('<tr id="places_area__row">.*?<td\s*class=["\']w2p_fw["\']>(.*?)</td>', html)[0]

fields = ('area', 'population', 'iso', 'country', 'capital',
          'continent', 'tld', 'currency_code', 'currency_name',
          'phone', 'postal_code_format', 'postal_code_regex',
          'languages', 'neighbours')

def re_scraper(html):
    results = {}
    for field in fields:
        results[field] = re.search('<tr id="places_%s__row">.*?<td class="w2p_fw">(.*?)</td>' % field, html).groups()[0]
    return results

def bs_scraper(html):
    soup = BeautifulSoup(html, "html.parser")
    results = {}
    for field in fields:
        results[field] = soup.find('table').find('tr', id='places_%s__row' % field).find('td', class_='w2p_fw').text
    return results

def lxml_scraper(html):
    tree = lxml.html.fromstring(html)
    results = {}
    for field in fields:
        results[field] = tree.cssselect('table > tr#places_%s__row > td.w2p_fw' % field)[0].text_content()
    return results

def main():
    NUM_ITERATIONS = 1000
    for name, scraper in [('Regular expresssions', re_scraper),
                          ('BeautifulSoup', bs_scraper),
                          ('Lxml', lxml_scraper)]:
        start = time.time()
        for i in range(NUM_ITERATIONS):
            if scraper == re_scraper:
                re.purge()
            result = scraper(html)
            assert(result['area'] == '244,820 square kilometres')
        end = time.time()
        print '%s: %.2f seconds' % (name, end - start)

if __name__ == '__main__':
    main()