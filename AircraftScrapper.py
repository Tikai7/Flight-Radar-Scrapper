import os
import pandas as pd
from Scrapper import Scrapper
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

class AircraftScrapper(Scrapper):
    def __init__(self) -> None:
        super().__init__()
        self.url = "https://www.flightradar24.com/data/aircraft"
        options = uc.ChromeOptions() 
        options.headless = False 
        self.driver = uc.Chrome(use_subprocess=True, options=options) 


    def _get_aircraft_data(self):

        if os.path.exists("data/Temp_Aircraft_Stats.csv"):
            aircraft_stats = pd.read_csv("data/Temp_Aircraft_Stats.csv").to_numpy()
        else:
            aircraft_stats = self._get_aircraft_stats().to_numpy()

        old_family = ""
        aircraft_family = dict()
        for _,_,family,url in aircraft_stats:
            if family != old_family:
                data = self._get_aircraft_stats_by_family(url)
                old_family = family
                aircraft_family[family] = data
        return self._get_df_from_data(aircraft_family)

    def _get_aircraft_stats(self):
        keys = {0 : "Aircraft", 1 :"Number", 2 :"Family"}
        aircraft_data = {
            "Aircraft" : [],
            "Number" : [],
            "Family" : [],
            "URL" : []
        }
        self.driver.get(self.url)
        aircraft_body = self.driver.find_element(By.CLASS_NAME,"table").find_element(By.TAG_NAME,"tbody")
        aircraft_lines = aircraft_body.find_elements(By.TAG_NAME,"tr")

        for tr in aircraft_lines:
            td = tr.find_elements(By.TAG_NAME,"td")
            if len(td) == 3:
                aircraft_class = td[0].text
                td = td[1:]
            elif len(td) == 1:
                continue            
            aircraft_data["Family"].append(aircraft_class)
            for i, td in enumerate(td):
                if i == 0:
                    aircraft_data["URL"].append(td.find_element(By.TAG_NAME,"a").get_attribute("href"))
                aircraft_data[keys[i]].append(td.text)

        df = pd.DataFrame.from_dict(aircraft_data)
        df.to_csv("data/Temp_Aircraft_Stats.csv",index=False)
        return df

    def _get_aircraft_stats_by_family(self,url):
        self.driver.get(url)
        tbody = self.driver.find_element(By.TAG_NAME,"tbody")
        lines = tbody.find_elements(By.TAG_NAME,"tr")
        aircraft = dict()
        for tr in lines:
            all_td = tr.find_elements(By.TAG_NAME,"td")
            aircraft_name = all_td[1].text
            aircraft_companies = all_td[3].text
            aircraft.setdefault(aircraft_name,set()).add(aircraft_companies)
        return aircraft
    
    def _get_df_from_data(self,aircraft_family):
        new_aircraft_stats = []
        aircraft_stats = pd.read_csv("data/Temp_Aircraft_Stats.csv").to_numpy()
        for aircraft, number, family, url in aircraft_stats:
            for family in aircraft_family.keys():
                if aircraft in aircraft_family[family]:
                    companies = aircraft_family[family][aircraft]
                    for company in companies:
                        new_aircraft_stats.append({
                            "Aircraft" : aircraft,
                            "Number" : number,
                            "Family" : family,
                            "Company" : company
                        })
                    break
        df = pd.DataFrame.from_dict(new_aircraft_stats)
        df.to_csv("data/Aircraft_Stats.csv",index=False)
        return df

    def scrappe(self):
        return self._get_aircraft_data()
    
scrapper = AircraftScrapper()
scrapper.scrappe()
