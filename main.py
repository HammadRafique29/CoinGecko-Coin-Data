import time
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CoinGecko:
    def __init__(self) -> None:
        pass

    def getdriver(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.headless = False
        chrome_options.arguments.extend(["--no-sandbox", "--disable-setuid-sandbox"])
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.add_argument('--disable-application-cache')
        chrome_options.add_argument('--disable-cache')
        chrome_options.add_argument('--disable-component-update')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--start-minimized")
        chrome_options.add_argument('--disable-features=OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction,OptimizationHints')
        self.driver = uc.Chrome(options=chrome_options)

    def getData(self):
        self.getdriver()
        coinRows = "//table[@data-controller='coin-row-ads']//tbody//tr"
        coin_xpath = "//a[contains(@href, 'en/coins')]//div[@class='tw-text-gray-700 dark:tw-text-moon-100 tw-font-semibold tw-text-sm tw-leading-5']"
        ranks_Xpath = "//table[@data-controller='coin-row-ads']//tbody//tr//td[2]"
        coinsNames_Xpath = "//table[@data-controller='coin-row-ads']//tbody//tr//td[3]"
        coinsHref_Xpath = "//table[@data-controller='coin-row-ads']//tbody//tr//td[3]//a"
        coinsPRice_Xpath = "//table[@data-controller='coin-row-ads']//tbody//tr//td[5]"
        coins24_Xpath = "//table[@data-controller='coin-row-ads']//tbody//tr//td[10]"

        self.data = {}
        self.data['coinsNames'] = []
        self.data['ranks'] = []
        self.data['coinsPRice'] = []
        self.data['coins24'] = []
        self.data['coinsHref'] = []

        for i in range(1, 5):
            self.driver.get(f"https://www.coingecko.com/?items=300&page={i}")	
            try:
                time.sleep(5)
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, ranks_Xpath)))
                ranks = [x.text for x in self.driver.find_elements(By.XPATH, ranks_Xpath)]
                coinsNames = [x.text for x in self.driver.find_elements(By.XPATH, coinsNames_Xpath)]
                coinsPRice = [x.text for x in self.driver.find_elements(By.XPATH, coinsPRice_Xpath)]
                coins24 = [x.text for x in self.driver.find_elements(By.XPATH, coins24_Xpath)]
                coinsHref = [x.get_attribute("href") for x in self.driver.find_elements(By.XPATH, coinsHref_Xpath)]
                
                self.data['coinsNames'] = self.data['coinsNames']+coinsNames
                self.data['ranks'] = self.data['ranks']+ ranks
                self.data['coinsPRice'] = self.data['coinsPRice']+coinsPRice
                self.data['coins24'] = self.data['coins24']+coins24
                self.data['coinsHref'] = self.data['coinsHref']+coinsHref
                
            except Exception as e:
                print(e)
        self.save_json()

    def read_json(self):
        with open('coinsData.json', 'r') as f:
            data = json.loads(f.read())
        return data
    
    def convert_to_json(self):
        res = {}
        for i in range(len(self.data['ranks'])):
            res[self.data['coinsNames'][i]] = [self.data['ranks'][i], self.data['coinsPRice'][i], self.data['coins24'][i], self.data['coinsHref'][i]]
        return res

    def save_json(self):
        res = self.convert_to_json()
        res = json.dumps(res)
        with open('coinsData.json', "w") as f:
            f.write(res)

    def write_excel(self):
        import pandas as pd
        json_data = self.convert_to_json()
        df = pd.DataFrame.from_dict(json_data, orient='index', columns=['Rank', 'Price', '24H Price', 'Link'])
        df.to_excel('coin_data.xlsx', index_label='Coin')

    def get_telegrams(self):

        self.getdriver()
        telegramLink = "//a[contains(@href, 't.me/')]"
        coinTelegramGroups = []
        res = self.read_json()

        limit = 0
        for coin in res.items():
            if limit==300: 
                print(coinTelegramGroups)
                input("Start")
            self.driver.get(coin[1][3])
            try: WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, telegramLink)))
            except: continue
            telegram = self.driver.find_elements(By.XPATH, telegramLink)
            if len(telegram) == 3: coinTelegramGroups.append(telegram[0].get_attribute("href"))
            else: continue
            limit+=1

        import pandas as pd
        df = pd.DataFrame(coinTelegramGroups, columns=["telegram"])
        df.to_excel('telegram_data.xlsx', index=False)

        # coinTelegramGroups = []
        # for link in coin_links:
        #     self.driver.get(link)
        #     try: WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, telegramLink)))
        #     except: continue
        #     telegram = self.driver.find_elements(By.XPATH, telegramLink)
        #     if len(telegram) == 3: coinTelegramGroups.append(telegram[0].get_attribute("href"))
        #     else: continue



if __name__ == "__main__":
    CoinGecko().get_telegrams()
