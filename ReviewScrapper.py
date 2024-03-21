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
from selenium.common.exceptions import NoSuchElementException

class ReviewScrapper():
    def __init__(self,file) -> None:
        self.file = file
        self.driver = webdriver.Chrome()

    def get_url_reviews(self):
        airlines = pd.read_csv(self.file,sep=',')
        urls_dict = airlines.groupby('Country')['URL'].agg(list).to_dict()
        return urls_dict

    
    def find_reviews(self):
        urls_dict = self.get_url_reviews()
        airports_name_file = pd.read_csv("Airports", sep=",")
        reviews_dict = dict()
        for country in urls_dict:
            airports_name = airports_name_file.loc[airports_name_file["Country"] == country, "Airport"].to_numpy()
            airports_name = [airport.split("(")[0].strip() for airport in airports_name]
            airports_name = [airport.replace('\t', ' ') for airport in airports_name]
            airports_name = [airport.replace('/', '_') for airport in airports_name]
            already_scrapped_airport = os.listdir("./data/Reviews")
            already_scrapped_airport.pop(0)
            already_scrapped_airport = [file.split("_")[1] for file in already_scrapped_airport]
            for airport, url in zip(airports_name,urls_dict[country]):
                if airport in already_scrapped_airport or airport == 'Karlsruhe_Baden-Baden Airport':
                    continue
                self.driver.get(url+'/reviews')
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
                reviews_dict[country] = self.get_reviews(airport_name.text)
                df_country = pd.DataFrame(reviews_dict[country], columns=["Date","Content", "General Stars", "Getting to the Airport", "Terminal facilities", "WiFi", "Food and retail services","Lounge","Immigration/customs","Baggage claim","Security check"])
                df_country.insert(0, 'Country', country)  # Add 'Country' column with the value 'Albania'
                df_country.to_csv(f'./data/Reviews/{country}_{airport}_Reviews', sep=',', index=False, encoding='utf-8')
                time.sleep(5)
        return reviews_dict
    
    def get_reviews(self,airport_name):
        comment = self.driver.find_elements(By.CSS_SELECTOR,"div.row.cnt-comment")
        general_stars = []
        date = []
        content = []
        s1_stars = [] #getting to the airport
        s2_stars = [] #terminal facilities
        s3_stars = [] #wifi
        s4_stars = [] #food and retail services
        s5_stars = [] #lounge
        s6_stars = [] #immigration/customs
        s7_stars = [] #baggage claims
        s8_stars = [] #security check
        
        for c in comment:
            stars = c.find_element(By.CSS_SELECTOR,"div.stars")
            general_stars.append(len(stars.find_elements(By.CSS_SELECTOR,"i.fa.fa-star.yellow")))
            date_elt = c.find_element(By.CSS_SELECTOR,"span.date.pull-right")
            date.append(date_elt.get_attribute("title"))
            content.append(c.find_element(By.CSS_SELECTOR,"div.content,div.content.ng-binding").text)
            subcat = c.find_elements(By.CSS_SELECTOR,"div.col-md-6.stars.m-t-xs.p-none,div.row.m-t-s.p-b-s.subratings.ng-hide")
        
            spans = []
            for s in subcat:
                try:
                    spans.append(s.find_element(By.CSS_SELECTOR,"span").text)
                    span = s.find_element(By.CSS_SELECTOR,"span.label").text
                    if span == "Getting to the airport":
                        s1_stars.append(len(s.find_elements(By.CSS_SELECTOR,"i.fa.fa-star.yellow")))
                    elif span == "Terminal facilities":
                        s2_stars.append(len(s.find_elements(By.CSS_SELECTOR,"i.fa.fa-star.yellow")))
                    elif span == "WiFi":
                        s3_stars.append(len(s.find_elements(By.CSS_SELECTOR,"i.fa.fa-star.yellow")))
                    elif span == "Food and retail services":
                        s4_stars.append(len(s.find_elements(By.CSS_SELECTOR,"i.fa.fa-star.yellow")))
                    elif span == "Lounge":
                        s5_stars.append(len(s.find_elements(By.CSS_SELECTOR,"i.fa.fa-star.yellow")))
                    elif span == "Immigration/customs":
                        s6_stars.append(len(s.find_elements(By.CSS_SELECTOR,"i.fa.fa-star.yellow")))
                    elif span == "Baggage claim":
                        s7_stars.append(len(s.find_elements(By.CSS_SELECTOR,"i.fa.fa-star.yellow")))
                    elif span == "Security check":
                        s8_stars.append(len(s.find_elements(By.CSS_SELECTOR,"i.fa.fa-star.yellow")))
                
                except NoSuchElementException:
                    spans.append(None)
            
            if "Getting to the airport" not in spans:
                s1_stars.append(None)
            if "Terminal facilities" not in spans:
                s2_stars.append(None)
            if "WiFi" not in spans:
                s3_stars.append(None)
            if "Food and retail services" not in spans:
                s4_stars.append(None)
            if "Lounge" not in spans:
                s5_stars.append(None)
            if "Immigration/customs" not in spans:
                s6_stars.append(None)
            if "Baggage claim" not in spans:
                s7_stars.append(None)
            if "Security check" not in spans:
                s8_stars.append(None)
        data= [[d.split(" ")[0],c,gs,s1,s2,s3,s4,s5,s6,s7,s8] for d,c,gs,s1,s2,s3,s4,s5,s6,s7,s8  in zip(date,content,general_stars, s1_stars,s2_stars,s3_stars,s4_stars,s5_stars,s6_stars,s7_stars,s8_stars)]
        return data 

    def create_dataframe(self):
        arrivals = self.find_reviews()
        transformed_data = [(country, *review) for country, reviews in reviews_dict.items() for review in reviews]
        pd.DataFrame(transformed_data, columns=["Country","Date","Content", "General Stars", "Getting to the Airport", "Terminal facilities", "WiFi", "Food and retail services","Lounge","Immigration/customs","Baggage claim","Security check"])
        return df
        
    def scrapper(self):
        df = self.find_reviews()
        self.driver.quit()
        return df