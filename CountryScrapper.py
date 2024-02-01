import bs4
import pandas as pd
import numpy as np
from urllib import request

class CountryScrapper():
    def __init__(self,url= "https://www.flightradar24.com/data/airports",headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}) -> None:
        self.url = url
        self.headers = headers
        req = request.Request(url, headers=self.headers)
        request_text = request.urlopen(req).read()
        self.page = bs4.BeautifulSoup(request_text, "html.parser")
        
    def get_table(self):
        return self.page.find("table", class_="tbl_datatable")
    
    def get_countries(self):
        table = self.get_table()
        tags = table.find_all("a",{"data-country": True})
        countries = [c.text for c in tags if c.text != ""]
        return countries
    
    def get_nb_airports(self):
        table = self.get_table()
        nb = table.find_all("span", class_="gray pull-right")
        airports_number = [''.join(char for char in span.text if char.isdigit()) for span in nb]
        return airports_number
    
    def create_dataframe(self):
        countries = self.get_countries()
        airports = self.get_nb_airports()
        return pd.DataFrame(list(zip(countries,airports)),columns=["Country","Airports"])
    
    def scrapper(self):
        df = self.create_dataframe()
        return df