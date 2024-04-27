import pandas as pd
from Scrapper import Scrapper
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

class LowCostScrapper(Scrapper):
    def __init__(self) -> None:
        super().__init__()
        self.url = 'https://fr.wikipedia.org/wiki/Liste_des_compagnies_a%C3%A9riennes_%C3%A0_bas_co%C3%BBts'
        options = uc.ChromeOptions() 
        options.headless = False 
        self.driver = uc.Chrome(use_subprocess=True, options=options) 

    def scrappe(self):
        low_cost_airlines = [ 
            "Nas Air", "Flyadeal", "Air Arabia", "flydubai", 
            "RAK Airways", "Wizz Air Abu Dhabi", "Petra Airlines","Wings Of Lebanon",
            "SalamAir", "Jazeera Airways", "Felix Airways"
        ]

        self.driver.get(self.url)
        all_continents = self.driver.find_elements(By.CLASS_NAME,"colonnes")

        for continent in all_continents:
            all_countries = continent.find_element(By.TAG_NAME,"ul").find_elements(By.TAG_NAME,"li")
            for country in all_countries:
                all_airlines = country.text
                try:
                    country, airlines = all_airlines.split(':')    
                    if country.strip() == "Kenya":
                        airlines = ["Fastjet", "Jambojet"]
                    else:
                        airlines = airlines.strip().split(",")
                    low_cost_airlines.extend(airlines)
                except:
                    continue
        
        df = pd.DataFrame(low_cost_airlines,columns=["Low Cost Airlines"])
        print(df)
        df.to_csv("data/Low_Cost_Airlines.csv",index=False)
LowCostScrapper().scrappe()