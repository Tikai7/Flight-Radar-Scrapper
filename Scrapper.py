class Scrapper():
    def __init__(self) -> None:
        self.url = "https://www.flightradar24.com/data/airports"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}