import numpy as np
import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DepArrScrapper():
    def __init__(self,file,choice) -> None:
        self.file = file
        self.choice = choice
        self.driver = webdriver.Chrome()

    def get_url_arrival(self):
        airlines = pd.read_csv(self.file,sep=',')
        urls_dict = airlines.groupby('Country')['URL'].agg(list).to_dict()
        return urls_dict

    
    def find_arrivals(self):
        urls_dict = self.get_url_arrival()
        airports_name_file = pd.read_csv("Airports", sep=",")
        arrivals = dict()
        for country in urls_dict:
            airports_name = airports_name_file.loc[airports_name_file["Country"] == country, "Airport"].to_numpy()
            airports_name = [airport.split("(")[0].strip() for airport in airports_name]
            already_scrapped_airport = os.listdir("./data")
            already_scrapped_airport.pop(0)
            already_scrapped_airport = [file.split("_")[1] for file in already_scrapped_airport]
            for airport, url in zip(airports_name,urls_dict[country]):
                if airport in already_scrapped_airport:
                    continue
                if self.choice == "arrivals":
                    self.driver.get(url+'/arrivals')
                elif self.choice == "departures":
                    self.driver.get(url+'/departures')
                self.wait = WebDriverWait(self.driver, 50)
                self.wait.until(EC.visibility_of_element_located((By.ID, 'data')))
                try:
                    button_cookie = self.driver.find_element(By.ID, "onetrust-reject-all-handler")
                    if button_cookie.is_displayed():
                        button_cookie.click()
                except:
                    pass
                buttons = self.driver.find_elements(By.CSS_SELECTOR,"button.btn.btn.btn-table-action.btn-flights-load")
                for button in buttons:
                    if button.is_displayed():
                        button.click()
                        time.sleep(1)
                    else:
                        continue
                airport_name = self.driver.find_element(By.CLASS_NAME,"airport-name")
                arrivals[country] = self.get_arrivals(airport_name.text)
                flattened_data = [flight for flight in arrivals[country]]
                df_country = pd.DataFrame(flattened_data, columns=["Airport", "Date", "Time", "Flight", "Airline", "Aircraft", "Aircraft Registration", "Status"])
                df_country.insert(0, 'Country', country)  # Add 'Country' column with the value 'Albania'
                if self.choice == "arrivals":
                    df_country.to_csv(f"./data/{country}_{airport}_Arrivals", sep=',', index=False, encoding='utf-8')
                elif self.choice == "departures":
                    df_country.to_csv(f"./data/{country}_{airport}_Departures", sep=',', index=False, encoding='utf-8')
                time.sleep(5)
        return arrivals
    
    def get_arrivals(self,airport_name):
        date = self.driver.find_elements(By.CSS_SELECTOR,"tr.hidden-xs.hidden-sm.ng-scope")
        heure_prevue = [d.find_element(By.CSS_SELECTOR, "td.ng-binding") for d in date]
        flight_number = self.driver.find_elements(By.CSS_SELECTOR,"td.p-l-s.cell-flight-number > a.notranslate.ng-binding")
        destination = self.driver.find_elements(By.CSS_SELECTOR,"span.hide-mobile-only.ng-binding")
        airline = self.driver.find_elements(By.CSS_SELECTOR,"td.cell-airline > a.notranslate.ng-binding")
        aircraft = self.driver.find_elements(By.CSS_SELECTOR,"span.notranslate.ng-binding")
        aircraft_registration = self.driver.find_elements(By.CSS_SELECTOR,"td > a.fs-10.fbold.notranslate.ng-binding")
        statut = self.driver.find_elements(By.CSS_SELECTOR, "td.ng-binding > span.ng-binding")
        statut2 = [stat.find_element(By.XPATH, "..") for stat in statut]
        date = [d.get_attribute("data-date") for d in date]
        data= [[airport_name,d,h.text,f.text,a.text,ai.text,a_info.text.strip("()"),s2.text] for d,h,f,a,ai,a_info,s2 in zip(date,heure_prevue,flight_number,airline,aircraft,aircraft_registration,statut2)]
        return data 
    
    def create_dataframe(self):
        arrivals = self.find_arrivals()
        transformed_data = [(country, *flight) for country, flights in arrivals.items() for flight in flights]
        df = pd.DataFrame(transformed_data, columns=["Country", "Airport", "Date", "Time", "Flight", "Airline", "Aircraft", "Aircraft Registration", "Status"])
        return df
    
    
    def scrapper(self):
        df = self.create_dataframe()
        self.driver.quit()
        return df