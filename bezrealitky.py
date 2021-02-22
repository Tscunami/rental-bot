from selenium import webdriver
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

CLICK_SLEEP_TIME = 0.25


class BezRealitky():
    def __init__(self):
        self.driver = webdriver.Chrome("C:\Shortcuts\Applications/chromedriver.exe")

    def start_searching(self):
        self.driver.get("https://www.bezrealitky.cz/")
        sleep(0.75)
        self.apply_filters()
        self.read_all_offers()
        self.download_html()

    def apply_filters(self):
        self.driver.find_element_by_id("a-type-pronajem").click()
        self.driver.find_element_by_id("a-type-byt").click()
        self.driver.find_element_by_id("locationInput").send_keys('Praha')
        self.driver.find_element_by_id("locationInput").submit()
        sleep(3)
        self.driver.find_element_by_id("priceFrom").send_keys(10000)
        sleep(CLICK_SLEEP_TIME)
        self.driver.find_element_by_id("priceTo").send_keys(20000)
        sleep(CLICK_SLEEP_TIME)
        self.driver.find_element_by_xpath("//*[@id='bzr-multiselect-estateType']/a").click()
        sleep(CLICK_SLEEP_TIME)
        self.driver.find_element_by_xpath("//*[@id='bzr-multiselect-estateType']/div/span[2]/label/span[2]").click()
        sleep(CLICK_SLEEP_TIME)
        self.driver.find_element_by_xpath("//*[@id='bzr-multiselect-disposition']/a").click()
        sleep(CLICK_SLEEP_TIME)
        # 3 + 1
        self.driver.find_element_by_xpath("//*[@id='bzr-multiselect-disposition']/div/span[7]/label/span[2]").click()
        # 4 + kk
        self.driver.find_element_by_xpath("//*[@id='bzr-multiselect-disposition']/div/span[8]/label/span[2]").click()
        # 4 + 1
        self.driver.find_element_by_xpath("//*[@id='bzr-multiselect-disposition']/div/span[9]/label/span[2]").click()
        # 5 + kk
        self.driver.find_element_by_xpath("//*[@id='bzr-multiselect-disposition']/div/span[10]/label/span[2]").click()
        # 5 + 1
        self.driver.find_element_by_xpath("//*[@id='bzr-multiselect-disposition']/div/span[11]/label/span[2]").click()
        # 6 + kk
        self.driver.find_element_by_xpath("//*[@id='bzr-multiselect-disposition']/div/span[12]/label/span[2]").click()
        # 6 + 1
        self.driver.find_element_by_xpath("//*[@id='bzr-multiselect-disposition']/div/span[13]/label/span[2]").click()
        sleep(CLICK_SLEEP_TIME)
        self.driver.find_element_by_xpath("//*[@id='search-content']/form/div[2]/div[2]/div[3]/div[1]/p/a/span[3]").click()
        self.driver.find_element_by_id("surfaceFrom").send_keys(80)
        self.driver.find_element_by_xpath("//*[@id='search-content']/form/div[2]/div[2]/div[3]/div[2]/p/button").click()
        sleep(4)
        self.driver.find_element_by_id("onetrust-accept-btn-handler").click()
        sleep(5)
        advertisement = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[11]/div/div/div[2]/div/a/img")))
        self.driver.execute_script("arguments[0].click();", advertisement)
        sleep(1)

    def read_all_offers(self):
        are_next_offers = True
        while are_next_offers:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            sleep(1)

            try:
                self.driver.find_element_by_css_selector("#search-content > form > div.b-filter__content "
                                                 "> div.b-filter__inner.pb-0 > div.row > div "
                                                 "> p > button").click()
            except NoSuchElementException:
                are_next_offers = False
            sleep(1)

    def download_html(self):
        html_content = self.driver.find_element_by_xpath("/html/body/div[1]/main/div/div/div[2]/form/div"
                                                         "[2]/div[4]").get_attribute('outerHTML')

        soup = BeautifulSoup(html_content, "html.parser")
        articles = soup.find_all(name="a", class_="product__link")
        prices = soup.find_all(name="strong", class_="product__value")

        all_links = [link.get("href") for link in articles]
        all_addresses = [address.getText() for address in articles]
        all_prices = [price.getText() for price in prices]

        self.send_data(addresses=all_addresses, prices=all_prices, links=all_links)

    def send_data(self, addresses, prices, links):

        for index in range(0, len(addresses)):
            self.driver.get("https://docs.google.com/forms/d/e/1FAIpQLSdYR-xloQsQdsHOSE9Kld4MO4OwbbqA7ehE2eDgevfQhe0e"
                            "6w/viewform?usp=sf_link")
            sleep(1)
            self.driver.find_element_by_xpath("/html/body/div/div[2]/form/div[2]/div/div[2]/div[1]/div/div/div[2]"
                                              "/div/div[1]/div/div[1]/input").send_keys(addresses[index])
            self.driver.find_element_by_xpath("/html/body/div/div[2]/form/div[2]/div/div[2]/div[2]/div/div/div[2]"
                                              "/div/div[1]/div/div[1]/input").send_keys(prices[index])
            self.driver.find_element_by_xpath("/html/body/div/div[2]/form/div[2]/div/div[2]/div[3]/div/div/div[2]"
                                              "/div/div[1]/div/div[1]/input").send_keys(links[index])
            sleep(0.25)
            self.driver.find_element_by_xpath("/html/body/div/div[2]/form/div[2]/div/div[3]/div[1]/div/div/span"
                                              "/span").click()


