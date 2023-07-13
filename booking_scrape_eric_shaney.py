#%%
#!pip3 install -r requirements.txt
#import dropbox
from selenium.webdriver.common.keys import Keys
# auxiliary functions modified by Luis.
import scrape_functions as kzd
import sys
import calendar
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
import re
from selenium.webdriver.support.ui import Select
import random
import time
from selenium import webdriver
import os
import numpy as np
import importlib
importlib.reload(sys.modules['scrape_functions'])
from datetime import date
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
import pandas as pd

# %% Starting code
dfolder = 'out'
link = 'https://www.booking.com/'
profile, browser, download_path = kzd.start_up(dfolder, link, download=True) 

#%% Main Page
place = 'Barcelona'
search1 = browser.find_element('xpath','//input[@placeholder="Where are you going?"]')
search1.send_keys(place)

# kzd.check_and_click(
#     browser, '.sb-searchbox__button', type='css')
kzd.check_and_click(browser,'//button[@type="submit"]', type='xpath')
print('main search button clicked')

#%% Search Page
time.sleep(2)
dates = browser.find_elements('xpath',
    '//table[@class="aadb8ed6d3"]/tbody/tr/td/span')
print('dates: ', len(dates))


#%%
time.sleep(2)
check_in_date = "2023-01-28"
check_out_date = "2023-01-31"

#%%
def scrollDown(driver, numberOfScrollDowns):
    body = driver.find_element(By.TAG_NAME, "body")
    while numberOfScrollDowns >= 0:
        body.send_keys(Keys.PAGE_DOWN)
        numberOfScrollDowns -= 1
    return driver

#%%
scrollDown(browser, 0.05)

e = browser.find_element(By.XPATH, '//span[@data-date="{}"]'.format(check_in_date))
browser.execute_script("arguments[0].click()", e)

e = browser.find_element(By.XPATH, '//span[@data-date="{}"]'.format(check_out_date))
browser.execute_script("arguments[0].click()", e)
time.sleep(1)

# click on empty space
kzd.check_and_click(
    browser, '//input[@class="ce45093752"]', type='xpath')
print('blank space clicked')

time.sleep(1)

kzd.check_and_click(browser,'//button[@type="submit"]', type='xpath')
print('search button clicked')

time.sleep(1)

#%% LOOPING OVER WEBPAGES:

"""
This function is to obtain total number of pages.
To loop, just insert the full code on a big loop and use the pages output.


ADDITION: You can also add random waiting times to avoid getting banned from webpages.
"""

def get_number_pages(browser):
    '''
    Get the number of pages. 
    '''
    a = browser.find_elements('xpath',
        '//button[text() and @class="fc63351294 f9c5690c58"]')
    total_pages = int(a[-1].text)
    time.sleep(1)
    return(total_pages)

pages = get_number_pages(browser)
print('total pages: ', pages)
#%%


def BookingReport(deal_boxes):
    page_report = []
    for deal_box in deal_boxes:
        hotel_name = deal_box.find_element(By.CSS_SELECTOR,
            'div[data-testid="title"]'
        ).get_attribute('innerHTML').strip()
        
        if not deal_box.find_elements(By.CSS_SELECTOR, 'span[data-testid="price-and-discounted-price"]'):
            hotel_price = deal_box.find_element(By.CSS_SELECTOR,
                'div[data-testid="price-and-discounted-price"]'
            ).find_element(By.TAG_NAME, 'div').get_attribute('innerHTML').strip()
        else:
            hotel_price = deal_box.find_element(By.CSS_SELECTOR,
                'span[data-testid="price-and-discounted-price"]'
            ).get_attribute('innerHTML').strip()
            hotel_price = hotel_price.replace("&nbsp;", "")
            hotel_price = hotel_price.replace(",", "")
            hotel_price = int(hotel_price.replace("€", ""))
        
        try:
            hotel_score = deal_box.find_element(By.CSS_SELECTOR,
                'div[aria-label*="Scored"]'
            ).get_attribute('innerHTML').strip()
        except:
            hotel_score = 'nan'
        page_report.append(
            [hotel_name, hotel_price, hotel_score]
        )
        # print([hotel_name, hotel_price, hotel_score])
    return page_report

#%%        
# Loop pages
full_report = []

for page in range(pages):
    # Get the list of hotel elements on the page

    print('Scraping page {} out of {}...'.format(page+1, pages))
    print('before: ', len(full_report))

    browser.implicitly_wait(2)
    
    deal_boxes = browser.find_elements(
            By.XPATH,
            "//div[@data-testid='property-card']"
            )
    report = BookingReport(deal_boxes)
    time.sleep(4)
    
    full_report.extend(report)
    
    print('after: ', len(full_report))

    scrollDown(browser, 1.5)

   
    kzd.check_and_click(browser, 
        '//button[@aria-label="Next page"]', 
        type='xpath' )
    
    time.sleep(4)

report_df = pd.DataFrame(full_report)

# %%
deal_boxes = browser.find_elements(
            By.XPATH,
            "//div[@data-testid='property-card']"
            )

report = BookingReport(deal_boxes)

# %%
