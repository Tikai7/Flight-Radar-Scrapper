import requests
from bs4 import BeautifulSoup
import AirPortScrapper

class ScraperWeather:
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.data = None
        self.airport_scrapper = AirPortScrapper.AirPortScrapper(url)

    def get_data(self):
        self.soup = BeautifulSoup(requests.get(self.url).text, 'html.parser')
        airports,urls_airports = self.airport_scrapper.find_airports()