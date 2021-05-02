from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
import re
from lxml.html import fromstring
import pandas as pd
pd.set_option('display.max_colwidth', 500)
import random

search_keyword = 'rosa'
base_url = 'https://www.wardow.com'
search_path = '/catalogsearch/result/?q='

def construct_url(base, path, keyword): 
    return base + path + keyword

class Search_Results_Scraper: 
    def __init__(self, url): 
        self.url = url 
    def get_html(self): 
        try: 
            response = requests.get(self.url)
            response.raise_for_status()
        except requests.RequestException: 
            print('A problem occurred with your request')
            raise
        html = fromstring(response.content)
        return html
    def get_search_results(self): 
        results = []
        results_display = {}
        page = self.get_html()
        page_results = page.findall('.//div[@class="product-tile__info"]')    
        for item in page_results: 
            item_title = item.xpath('.//a/@title')[0]
            item_url = item.xpath('.//a/@href')[0]
            if search_keyword in item_title.lower(): 
                results.append(item_url)
                results_display[item_title] = item_url 
        next_page = base_url + page.xpath('//button[@class="button btn-subtle next"]/@value')[0]
        print('Your search term has found the following results:')
        print(pd.DataFrame.from_dict(results_display, orient='index', columns=['url']))
        try: 
            get_search_results(get_html(next_page))
        except: 
            print('No further results pages could be found...')
        return results 

search_results = Search_Results_Scraper(construct_url(base_url, search_path, search_keyword))
results = search_results.get_search_results()

def generate_random_url(): 
    random_index = random.randint(0, len(results))
    return results[random_index]

class Scraper: 
    def __init__(self, url): 
        self.url = url
    def get_product_info(self):
        driver = webdriver.Chrome(executable_path=r'C:\Users\Maria\chromedriver\chromedriver.exe')
        driver.get(self.url)
        product_url = self.url
        title = driver.find_element_by_xpath('//span[@class="product-name"]').text
        product_id = driver.find_element_by_xpath('//span[@itemprop="sku"]').text
        product_image_urls = [img.get_attribute('src') for img in driver.find_elements_by_xpath('//img[@class="gallery-image"]')]
        brand = driver.find_element_by_xpath('//span[@itemprop="brand"]').text
        price = driver.find_element_by_xpath('//span[contains(@id, "product-price")]').text
        prediscount_price = driver.find_element_by_xpath('//span[contains(@id, "old-price")]').text
        category = driver.find_element_by_xpath('//ul[@itemprop="breadcrumb"]//a').text
        product_description = driver.find_element_by_xpath('//dd[@class="tab-container tab-description current"]').text
        try: 
            in_stock = bool(driver.find_element_by_xpath('//p[@class="availability in-stock"]/span').text)
        except:
            print('Product out of stock!')
        finally: 
            driver.quit()
        print('Product Info for your requested page:')
        return pd.DataFrame.from_dict(locals(), orient='index', columns=['product_info']).drop(index=['self', 'driver'])

scraper = Scraper(generate_random_url())
scraper.get_product_info()