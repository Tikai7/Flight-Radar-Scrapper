import bs4
import pandas as pd
import numpy as np
from urllib import request
import time
import time
class AirPortScrapper():
    def __init__(self,url = "https://www.flightradar24.com/data/airports",headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}) -> None:
        self.url = url
        self.headers = headers
        req = request.Request(url, headers=self.headers)
        request_text = request.urlopen(req).read()
        self.page = bs4.BeautifulSoup(request_text, "html.parser")

    def get_table(self):
        return self.page.find("table", id="tbl-datatable").find('tbody')
    
    def get_url_airport(self):
        url_list = []
        table = self.get_table()
        a_tags= table.find_all("a",{"data-country": True})
        url_list = np.unique([tag['href'] for tag in a_tags])
        return url_list
    
    def find_airports(self):
        url_list = self.get_url_airport()
        airports = dict()
        urls_airports = dict()
        for url in url_list:
            req = request.Request(url, headers=self.headers)
            request_text = request.urlopen(req).read()
            page_airports = bs4.BeautifulSoup(request_text,"html.parser")
            country = url.split("/")[-1].capitalize()
            airports[country] = self.get_airport(page_airports)
            urls_airports[country] = self.get_url(page_airports)
            time.sleep(5)
        return airports,urls_airports
    
    def get_airport(self,page):
        return [a_tag.find_parent().text for table_a in page.find_all("table", id="tbl-datatable") for a_tag in table_a.find_all('img', class_='icon-airport')]
    
    def get_url(self,page):
        return [a_tag.find_parent()['href'] for table_a in page.find_all("table", id="tbl-datatable") for a_tag in table_a.find_all('img', class_='icon-airport')]
    
    def create_dataframe(self):
        airports = self.find_airports()
        data_list = [{'Pays': country, 'Aéroport': ai} for country, airport in airports.items() for ai in airport]
        return pd.DataFrame(data_list)
    
    def scrapper(self):
        df = self.create_dataframe()
        return df