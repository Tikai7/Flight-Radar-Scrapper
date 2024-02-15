import numpy as np
import time
import pandas as pd
from Scrapper import Scrapper
from selenium.webdriver.common.by import By
from metar import Metar
import undetected_chromedriver as uc
from datetime import datetime
import os

class WeatherScrapper(Scrapper):
    def __init__(self):
        super().__init__()
        self.data = None
        self.MAX_ERROR = 7
        self.timeout = 10
        options = uc.ChromeOptions() 
        options.headless = False  # Set headless to False to run in non-headless mode
        self.driver = uc.Chrome(use_subprocess=True, options=options) 

    @staticmethod
    def decode_metar(metar_data):
        return Metar.Metar(metar_data).string()

    def _convert_to_dataframe(self, data):
        """
            Convert the list of data into a dataframe
            :param data: list of data
            :return: dataframe
        """
        flattened_data = []
        for entry in data:
            flattened_entry = {
                "country": entry["country"],
                "airport": entry["airport"],
                "METARs": entry["weather"]["METARs"],
                "UTC/Time": entry["weather"]["UTC/Time"],
            }
            flattened_data.append(flattened_entry)
        df = pd.DataFrame(flattened_data)
        date = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
        df.to_csv(f"data/Airports_Weather_{date.strip()}.csv", index=False)
        return df
        
    def _get_weather_data(self):
        """
            Get the weather data for each airport
            :return: list of weather data
        """
        airports_name = pd.read_csv("data/Airports_Name.csv", sep=",")
        airports_url = pd.read_csv("data/Airports_URL.csv", sep=",")
        # Group the airports by country and get the list of urls, ex : {'France': ['url1', 'url2', ...], 'USA': ['url1', 'url2', ...], ...}
        airports_url_list = airports_url.groupby("Country")["URL"].agg(list).to_dict()
        # Create a dictionary to store the number of errors for each airport (if the airport has more than 1/3 of errors, we skip it)
        countries_error = {airport:0 for airport in airports_url_list.keys()}

        airports_url["URL"] += "/weather"
        airports_url = airports_url.to_numpy()
        airports_name = airports_name["Airport"].to_numpy()

        # Get the last scrapped file to check if the airport has already been scrapped
        last_scrapped_file = os.listdir("data")[-2]
        df_temp = pd.read_csv(f"data/{last_scrapped_file}", sep=",")
        already_scrapped_country = list(set(df_temp["country"]))
        already_scrapped_country.sort()

        all_weather_data = []   
        old_country = ""

        for airport,(country, url) in zip(airports_name, airports_url):
            if country in already_scrapped_country or np.searchsorted(already_scrapped_country,country) < len(already_scrapped_country) or countries_error[country] > min(self.MAX_ERROR, len(airports_url_list[country])//4):
                continue

            state, data = self._get_airport_weather(url)
            if state:
                all_weather_data.append({
                    "country" : country, 
                    "airport" : airport, 
                    "weather" : data
                })
            else:
                print(country, "has", countries_error[country], "/", min(self.MAX_ERROR, len(airports_url_list[country])//4), "errors")
                countries_error[country] += 1
            
            if old_country != country:
                self._convert_to_dataframe(all_weather_data)
                old_country = country
                
                
            time.sleep(self.timeout)
        
        return self._convert_to_dataframe(all_weather_data)

    def _get_airport_weather(self, url):
        """
            Get the weather data for a specific airport
            :param url: url of the airport
            :return: weather data
        """
        try:
            keys =  {0:"METARs", 1:"UTC/Time"}
            weather_data = {"METARs":[], "UTC/Time":[]}
            self.driver.get(url)
            tbody = self.driver.find_element(By.CLASS_NAME, "table").find_element(By.TAG_NAME, "tbody")
            lines = tbody.find_elements(By.CLASS_NAME, "master")
            for tr in lines:
                for i,td in enumerate(tr.find_elements(By.TAG_NAME, "td")):
                    weather_data[keys[i]].append(td.text)
            print("Ok")
            return True,weather_data
        except:
            print("No weather data found")
            return False,1
        
    def scrappe(self):
        self.data = self._get_weather_data()
        return self.data
    

scrapper = WeatherScrapper()
scrapper.scrappe()
