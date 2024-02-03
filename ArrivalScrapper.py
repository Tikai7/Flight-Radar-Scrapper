import numpy as np
import time
import pandas as pd
from selenium import webdriver
class ArrivalScrapper():
    def __init__(self,file) -> None:
        self.file = file
        self.driver = webdriver.Chrome()
        
    def get_url_arrival(self):
        airlines = pd.read_csv(self.file,sep=',')
        urls_dict = airlines.groupby('Pays')['URL'].agg(list).to_dict()
        return urls_dict

    def find_arrivals(self):
        urls_dict = self.get_url_arrival()
        arrivals = dict()
        for country in urls_dict:
            for url in urls_dict[country]:
                self.driver.get(url+'/arrivals')
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