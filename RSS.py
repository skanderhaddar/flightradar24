from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd
from functools import partial
def scrape_flight_data (airport_code) :
    chrome_options = Options()
   # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options = chrome_options)
    airport_url = "https://www.flightradar24.com/data/airports/"+airport_code+"/arrivals"
    try:
        driver.get(airport_url)

        # Wait for the button to appear and accept cookies
        time.sleep(1)
        try:
            button1 = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
            button1.click()
        except NoSuchElementException:
            pass  # If the accept cookies button is not found, continue without clicking
        
        def click_button(ButtonName):
            # Wait for the button to be clickable
            try : 
                WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f'//button[contains(@class, "btn-flights-load") and contains(text(), "{ButtonName}")]'))
            )
            except : 
                pass

            # Click the button
            k =0
            while k <50:
                try:
                    button = driver.find_element(By.XPATH, f'//button[contains(@class, "btn-flights-load") and contains(text(), "{ButtonName}")]')
                    button.click()
                    time.sleep(3)  # Adjust the sleep time according to your needs
                    k =k+1
                except (ElementClickInterceptedException, ElementNotInteractableException):
                    break
        element = driver.find_elements(By.XPATH,'//*[@id="cnt-data-content"]/div/div[2]/div/aside/div[1]/table/tbody/tr[2]')
        for e in element:
            print(len(element))
            soup = e.get_attribute('outerHTML')
            sp = BeautifulSoup(soup, 'html.parser')
            tr_element = sp.find('tr')
            # Get the value of the class attribute
            class_value = tr_element.get('class')
            if (len(class_value) >0):
            # Wait for the "Load later flights" button to be clickable
                click_button("Load later flights")
                page_source = driver.page_source
                driver.quit()
                # Find all flight information rows
                soup2 = BeautifulSoup(page_source, 'html.parser')
                flight_rows = soup2.find_all('tr', class_='hidden-xs hidden-sm ng-scope')
                #flight_rows = soup2.find_elements(By.XPATH, '//tr[@class="hidden-xs hidden-sm ng-scope"]')
                flight_data = []
                for row in flight_rows:
                    data_date = row.get('data-date', 'N/A')
                    # Extract flight time
                    flight_time_tag = row.find('td', class_='ng-binding')
                    flight_time = flight_time_tag.text.strip() if flight_time_tag else 'N/A'

                    # Extract origin airport
                    origin_airport_tag = row.find('div', {'ng-show': '(objFlight.flight.airport.origin)'})
                    origin_airport = origin_airport_tag.find('a', class_='ng-binding')['title'] if origin_airport_tag else 'N/A'

                    # Extract flight number
                    flight_number_tag = row.find('a', class_='notranslate ng-binding')
                    flight_number = flight_number_tag.text.strip() if flight_number_tag else 'N/A'

                    # Extract aircraft model
                    aircraft_model_tag = row.find('span', class_='notranslate ng-binding')
                    aircraft_model = aircraft_model_tag.text.strip() if aircraft_model_tag else 'N/A'

                    # Extract flight status
                    flight_status_tag = row.find('span', class_='ng-binding', attrs={'ng-bind-html': 'objFlight.flight.statusMessage.text | unsafe'})
                    flight_status = flight_status_tag.text.strip() if flight_status_tag else 'N/A'

                    # Extract arrival time
                    arrival_time_td = row.find_all('td', class_='ng-binding')[1]
                    time_arrival = arrival_time_td.text.strip().split()[-1] if arrival_time_td else 'Time not found.'

                    # Extract aircraft
                    aircraft_tag = row.find_all('a', class_='notranslate ng-binding')[1]
                    aircraft = aircraft_tag.text.strip() if aircraft_tag else 'N/A'
                    # Append data to the list as a dictionary
                    flight_data.append({
        "Date": data_date,
        "Flight Time": flight_time,
        "Aircraft": aircraft,
        "Origin Airport": origin_airport,
        "flight": flight_number,
        "Aircraft Model": aircraft_model,
        "Flight Status": flight_status,
        "time_arrival":time_arrival})
                df = pd.DataFrame(flight_data)
                return (df)
            else : 
                return "we don't have any data for this ariport" 


    finally:
        pass

def find_new_rows(df2,df1):
    df1.reset_index(drop=True, inplace=True)
    df2.reset_index(drop=True, inplace=True)

    try:
        row = df2.iloc[-1]
        index = df1.index[df1.apply(lambda x: x.equals(row), axis=1)].tolist()[0]
        
    except IndexError:
        row = df2.iloc[-2]
        index = df1.index[df1.apply(lambda x: x.equals(row), axis=1)].tolist()[0]
        
    return pd.DataFrame(df1[index+1:])

def get_new_flights(duré):
    #Définir la fonction de scraping partielle pour "tun"
    scrape_data_tun = partial(scrape_flight_data, "tun")
    # Fonction pour exécuter la tâche et récupérer un nouveau DataFrame toutes les 30 minutes
    # Boucle pour exécuter la tâche et récupérer le nouveau DataFrame toutes les 30 minutes
    old_data = scrape_data_tun()
    while True:
        time.sleep(duré * 60)
        new_data = scrape_data_tun()
        added_data= find_new_rows(old_data, new_data )
        returned_data = old_data
        old_data= new_data
        return added_data , new_data , returned_data


