# -*- coding: UTF-8 -*-
from selenium import webdriver


def search():
    url = 'http://example.webscraping.com/places/default/search'
    driver = webdriver.Chrome()
    driver.get(url)
    driver.find_element_by_id('search_term').send_keys('.')
    js = "document.getElementById('page_size').options[1].text='260'"
    driver.execute_script(js)
    driver.find_element_by_id('search').click()
    driver.implicitly_wait(30)                      # 设置超时
    links = driver.find_elements_by_css_selector('#results a')
    countries = [link.text for link in links]
    print countries
    driver.close()

def dynamic():
    url = 'http://example.webscraping.com/places/default/dynamic'
    driver = webdriver.Chrome()
    driver.get(url)
    print driver.find_element_by_css_selector('#result').text
    driver.close()

if __name__ == '__main__':
    search()
    dynamic()