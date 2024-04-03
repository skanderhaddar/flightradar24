from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.options import Options
import pandas as pd
from  get_country import get_country
from  scrape_all_countries_airports import scrape_airport_data
def scrape_flight_data (airport_code) :
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options = chrome_options)
    airport_url = "https://www.flightradar24.com/data/airports/"+airport_code+"/arrivals"
    try:
        driver.get(airport_url)

        # Wait for the button to appear and accept cookies
        time.sleep(3)
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
            soup = e.get_attribute('outerHTML')
            sp = BeautifulSoup(soup, 'html.parser')
            tr_element = sp.find('tr')
            # Get the value of the class attribute
            class_value = tr_element.get('class')
            if (len(class_value) >0):
            # Wait for the "Load later flights" button to be clickable
               # click_button("Load later flights")
                #time.sleep(3)
               # click_button("Load earlier flights")
               # time.sleep(3)
                # Find all flight information rows
                flight_rows = driver.find_elements(By.XPATH, '//tr[@class="hidden-xs hidden-sm ng-scope"]')
                flight_data = []
                for row in flight_rows:
                    soup = row.get_attribute('outerHTML')
                    sp = BeautifulSoup(soup, 'html.parser')
                    tr_tag = sp.find('tr', {'class': 'hidden-xs hidden-sm ng-scope'})
                    # Extract the value of the 'data-date' attribute
                    if tr_tag :
                        data_date = tr_tag.get('data-date')
                    else : 
                        data_date = "N/A" 
                
                    flight_time_tag = sp.find('td', class_='ng-binding')
                    if flight_time_tag : 
                        flight_time = flight_time_tag.text.strip()
                    else : 
                        flight_time ="N/A"
                    # Find the div tag with ng-show="(objFlight.flight.airport.origin)"
                    div_tag = sp.find('div', {'ng-show': '(objFlight.flight.airport.origin)'})
                    # If the div tag is found, extract the origin airport
                    if div_tag:
                        origin_airport = div_tag.find('a', class_='ng-binding')['title']
                    else:
                        origin_airport = "N/A"                
                    flight_tag = sp.find('a', class_='notranslate ng-binding')
                    if flight_tag : 
                        flight = flight_tag.text.strip()
                    else : 
                        flight ="N/A"
                
                    aircraft_model_tag = sp.find('span', class_='notranslate ng-binding')
                    if aircraft_model_tag : 
                        aircraft_model = aircraft_model_tag.text.strip()
                    else : 
                        aircraft_model = "N/A"

                    flight_status_tag =sp.find('span', class_='ng-binding', attrs={'ng-bind-html': 'objFlight.flight.statusMessage.text | unsafe'})
                    if flight_status_tag : 
                        flight_status = flight_status_tag.text.strip()
                    else : 
                        flight_status= "N/A"
                    # Find the <td> tag containing the time
                    td_elements = sp.find_all('td', class_='ng-binding')
                    # Extract the text from the second <td> element
                    if len(td_elements) > 1:
                        time_arrival = td_elements[1].text.split()[-1]
                    else:
                        time_arrival="Time not found."
                    # Find all <a> tags with class "notranslate ng-binding"
                    a_tags = sp.find_all('a', class_='notranslate ng-binding')
                    # Extract the text content of the second <a> tag (index 1)
                    if len(a_tags) >= 2:
                        aircraft = a_tags[1].text.strip()
                    else:
                        aircraft = "N/A"
                    # Append data to the list as a dictionary
                    flight_data.append({
        "Date": data_date,
        "Flight Time": flight_time,
        "Aircraft": aircraft,
        "Origin Airport": origin_airport,
        "flight": flight,
        "Aircraft Model": aircraft_model,
        "Flight Status": flight_status,
        "time_arrival":time_arrival})
                df = pd.DataFrame(flight_data)
                return (df)
            else : 
                return "we don't have any data for this ariport" 


    finally:
            time.sleep(30)
            driver.quit()

def scrape_flight_from_country (country_name):
    url_country = "https://www.flightradar24.com/data/airports/" + country_name
    IATA , aeroport_names = scrape_airport_data(url_country)
    data_total_country = []
    for i, j in  zip (IATA, aeroport_names) : 
        df_aeroport = scrape_flight_data(i) 
        if isinstance(df_aeroport, pd.DataFrame):
            df_aeroport["Destination Aeroport"] =  j 
            data_total_country.append(df_aeroport)
    if len(data_total_country) >0 :
        concatenated_df = pd.concat(data_total_country, ignore_index=True)
        return concatenated_df
        
def scrape_all_arrival_flight() :
    countries = get_country()
    k = 0
    for country in countries :
        if country not in ["Curacao","Grenada","Guatemala","Chad", "Northern-Mariana-Islands" , "Nauru","Ethiopia", "Singapore","Democratic-Republic-Of-The-Congo","Libya","Benin","Bosnia-And-Herzegovina","United-Arab-Emirates","Cape-Verde","Tonga","Russia", "Papua-New-Guinea","Sierra-Leone" ]:
            print("start of extract data from :", country)
            data = scrape_flight_from_country(country) 
            print("End of extract data from :", country)
            return data
            break

            # File path to save the CSV data
            #file_path = f'C:/Users/USER/Desktop/arrival_flights/{country}_flights.csv'
            # Save the DataFrame to a CSV file
            #if isinstance(data, pd.DataFrame) :
                #data.to_csv(file_path, index=False)
                
        
