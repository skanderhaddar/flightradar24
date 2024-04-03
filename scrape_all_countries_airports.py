
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver

def scrape_airport_data(country_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options = chrome_options)

    try:
        driver.get(country_url)

        # Find all airport links
        IATA = []
        airport_names = []
        airport_links = driver.find_elements(By.CSS_SELECTOR, 'a[data-iata][data-lat][data-lon]')
        for airport_link in airport_links:
            airport_name = airport_link.text.strip().split('\n')[0]
            airport_iata = airport_link.get_attribute('data-iata')
            airport_icao = airport_name.split('(')[-1].split(')')[0]
            IATA.append(airport_iata)
            airport_names.append(airport_name)
        airport_names_cleaned = [airport.split(' (')[0] for airport in airport_names]

        

    finally:
        driver.quit()
    return IATA , airport_names_cleaned


def scrape_all_countries_airports(main_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options = chrome_options)

    try:
        driver.get(main_url)

        # Find all links to countries
        country_links = driver.find_elements(By.CSS_SELECTOR, 'table#tbl-datatable a[href^="https://www.flightradar24.com/data/airports/"]')
        AEROPORT_IATA = {}
        for country_link in set(country_links):
            country_url = country_link.get_attribute("href")
            for elem in scrape_airport_data(country_url)[0] : 
                AEROPORT_IATA[elem] = country_url[44:]

    finally:
        driver.quit()
    return AEROPORT_IATA
