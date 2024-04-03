from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.options import Options
import pandas as pd
def get_country():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options = chrome_options)
    try:
        url = "https://www.flightradar24.com/data/airports"
        driver.get(url)
        # Find all links to countries
        country_links = driver.find_elements(By.CSS_SELECTOR, 'table#tbl-datatable a[href^="https://www.flightradar24.com/data/airports/"]')
        country = []
        # Extract and print the country names
        for country_link in country_links:
            country_name = country_link.get_attribute("title")
            country.append(country_name.replace(" ", "-").replace("(", "").replace(")", ""))
        country_set = set(country)
    finally:
        driver.quit()
        return (country_set)