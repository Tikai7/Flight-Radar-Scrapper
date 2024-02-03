import time
import pandas as pd
from Scrapper import Scrapper
from selenium import webdriver
from selenium.webdriver.common.by import By
from metar import Metar

class ScraperWeather(Scrapper):
    def __init__(self):
        super().__init__()
        self.data = None
        self.driver = webdriver.Chrome()

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
        df.to_csv("data/Weather.csv", index=False)
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

        all_weather_data = []
        for airport,(country, url) in zip(airports_name, airports_url):
            if countries_error[country] > len(airports_url_list[country])//3:
                continue
            state, data = self._get_airport_weather(url)
            if state:
                all_weather_data.append({
                    "country" : country, 
                    "airport" : airport, 
                    "weather" : data
                })
            else:
                print(country, "has", countries_error[country], "/", len(airports_url_list[country])//3, "errors")
                countries_error[country] += 1
            time.sleep(self.timeout)
            if len(all_weather_data) == 4:
                break

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
            return True,weather_data
        except:
            print("No weather data found")
            return False,1
        
    def scrappe(self):
        self.data = self._get_weather_data()
        return self.data