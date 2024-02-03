import requests
from bs4 import BeautifulSoup
from AirPortScrapper import AirPortScrapper
from Scrapper import Scrapper

class ScraperWeather(Scrapper):
    def __init__(self):
        super().__init__()
        self.soup = None
        self.data = None
        self.airport_scrapper = AirPortScrapper(self.url, self.headers)

    def get_data(self):
        self.soup = BeautifulSoup(requests.get(self.url).text, 'html.parser')
        a,u = self.airport_scrapper.find_airports()
        return a,u

    def scrappe(self):
        pass

scrapper = ScraperWeather()
a,u = scrapper.get_data()
print(a)