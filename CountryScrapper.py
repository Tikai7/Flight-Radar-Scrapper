import bs4
import pandas as pd
import urllib
import numpy as np

from urllib import request

class CountryScrapper():
    def __init__(self,url,headers) -> None:
        self.url = url
        self.headers = headers
        req = request.Request(url, headers=self.headers)
        request_text = request.urlopen(req).read()
        self.page = bs4.BeautifulSoup(request_text, "html.parser")
        
    def get_table(self):
        return self.page.find("table", class_="tbl_datatable")
    
    def get_countries(self):
        tags = table.find_all("a",{"data-country": True})
        countries = [c.text for c in tags if c.text != ""]
        return countries
    
    def get_nb_airports(self):
        nb = table.find_all("span", class_="gray pull-right")
        airports_number = [''.join(char for char in span.text if char.isdigit()) for span in nb]
    
    def create_dataframe(self):
        countries = self.get_countries()
        airports = self.get_nb_airports()
        return pd.DataFrame(list(zip(countries,airports)),columns=["Country","Airports"])
    
    def scrapper(self):
        table = self.get_table()
        airports = self.get_countries()
        nb_airports = self.get_nb_airports()
        df = self.create_dataframe()
        return df