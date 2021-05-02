from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time
import re
import pandas as pd
pd.set_option('display.max_colwidth', 500)
import random

CHROMEDRIVER_PATH = r'C:\Users\Maria\chromedriver\chromedriver.exe'
streaming_url = 'https://www.pelitorrent.com/'
search_keyword = 'rey'

class Search_Results_Scraper: 
    def __init__(self, url): 
        self.url = url 
        self.results = []
    def get_results_page(self):
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH)
        driver.get(self.url)
        search_bar = driver.find_element_by_id('tr_live_search')
        search_bar.send_keys(search_keyword)
        search_bar.send_keys(Keys.RETURN)
        time.sleep(3)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)
        current_url = driver.current_url
        driver.quit()
        return current_url
    def get_search_results(self):      
        search_results = {}
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH)
        driver.get(self.get_results_page())
        entries = driver.find_elements_by_xpath('//ul[contains(@class, "post-lst")]//article[@class="post dfx fcl movies"]')
        for entry in entries: 
            entry_url = entry.find_element_by_class_name('lnk-blk').get_attribute('href')
            entry_title = entry.find_element_by_class_name('entry-title').text
            if search_keyword in entry_title.lower(): 
                self.results.append(entry_url)
                search_results[entry_title] = entry_url
        next_page_link = driver.find_element_by_link_text('SIGUIENTE')
        try:
            next_page_link.click()
            time.sleep(3)
            next_page = driver.current_url 
            get_search_results(next_page)
        except: 
            print('No further results for this search term could be found')
            driver.quit()
        finally: 
            driver.quit()
            print('Your search term has found the following results:')
            print(pd.DataFrame.from_dict(search_results, orient='index', columns=['url']))
        return 

results_scraper = Search_Results_Scraper(streaming_url)
results_scraper.get_search_results()

search_results = Search_Results_Scraper()
results = search_results.get_search_results()

def generate_random_url(): 
    random_index = random.randint(0, len(results_scraper.results))
    return results_scraper.results[random_index]

generate_random_url()

def get_link_info(url):
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH)
    driver.get(url)
    movie_title = driver.find_element_by_xpath('//h1').text
    movie_duration = driver.find_element_by_xpath('//span[@class="duration fa-clock far"]').text
    movie_poster_image_url = driver.find_element_by_xpath('//div[@class="post-thumbnail alg-ss"]//img').get_attribute('src')
    director = driver.find_element_by_xpath('//span[text()="Director"]/following-sibling::p/a').text
    director_url = driver.find_element_by_xpath('//span[text()="Director"]/following-sibling::p/a').get_attribute('href')
    cast_members = [element.text for element in driver.find_elements_by_xpath('//span[text()="Actores"]/following-sibling::p/a')]
    download_button = driver.find_element_by_xpath('//button[@data-mdl="mdl-download"]/span')
    time.sleep(5)
    download_button.click()
    time.sleep(5)
    download_info = driver.find_elements_by_xpath('//div[@class="download-links"]//tbody/tr/td')
    download_link_language = download_info[1].text
    download_link_quality = download_info[2].text
    download_link = driver.find_element_by_xpath('//a[@class="btn sm rnd blk"]').get_attribute('href')    
    driver.quit()
    print('Download link and info for your requested movie page:')
    return pd.DataFrame.from_dict(locals(), orient='index', columns=['movie_info']).drop(
        index=['driver', 'download_button', 'download_info']
    )