from selenium import webdriver
from time import sleep
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from my_selectors import *

STANDARD_WAIT_TIME = 3
CLICK_SLEEP_TIME = 0.25
CITY = 'Praha'
PRICE_FROM = 10000
PRICE_TO = 20000
ALL_DISPOSITIONS = [num for num in range(7, 14)]  # 3+1, 4+kk, 5+kk, 5+kk, 5+1, 6+kk, 6+1
SURFACE_FROM = 80


class BezRealitky():
    def __init__(self):
        self.option = webdriver.ChromeOptions()
        self.option.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(executable_path="C:\Shortcuts\Applications/chromedriver.exe",
                                       chrome_options=self.option)

    def perform_action(self, name, action, selector, wait_time=STANDARD_WAIT_TIME):
        if action == "click":
            if selector == "id":
                try:
                    WebDriverWait(self.driver, wait_time).until(
                        EC.element_to_be_clickable((By.ID, name))).click()
                except TimeoutException:
                    print(f"{name} element not loaded")
                except ElementClickInterceptedException:
                    print(f"{name} element raised ElementClickInterceptedException")

            elif selector == "xpath":
                try:
                    WebDriverWait(self.driver, wait_time).until(
                        EC.element_to_be_clickable((By.XPATH, name))).click()
                except TimeoutException:
                    print(f"{name} element not loaded")
                except ElementClickInterceptedException:
                    print(f"{name} element raised ElementClickInterceptedException")
        else:
            try:
                WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((By.ID, name))).send_keys(action)
            except TimeoutException:
                print(f"{name} element not loaded")
            except ElementClickInterceptedException:
                print(f"{name} element raised ElementClickInterceptedException")

    def start_searching(self):
        self.driver.get("https://www.bezrealitky.cz/")
        sleep(0.75)
        self.apply_filters()
        self.read_all_offers()
        self.download_html()

    def close_advertisement(self):
        advertisement = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[11]/div/div/div[2]/div/a/img")))
        self.driver.execute_script("arguments[0].click();", advertisement)

    def apply_filters(self):
        self.driver.find_element_by_id(TYPE_PRONAJEM_ID).click()
        self.driver.find_element_by_id(TYPE_BYT_ID).click()
        self.driver.find_element_by_id(LOCATION_INPUT_ID).send_keys(CITY)
        self.driver.find_element_by_id(LOCATION_INPUT_ID).submit()

        self.perform_action(PRICE_FROM_ID, PRICE_FROM, "id")
        self.perform_action(PRICE_TO_ID, PRICE_TO, "id")
        self.perform_action(TYPE_OF_HOUSING_XPATH, "click", "xpath")
        self.perform_action(SELECT_DUM_XPATH, "click", "xpath")
        self.close_advertisement()
        self.perform_action(TYPE_OF_DISPOSITION_XPATH, "click", "xpath")
        for disposition in ALL_DISPOSITIONS:
            self.perform_action(
                f"//*[@id='bzr-multiselect-disposition']/div/span[{disposition}]/label/span[2]",
                "click",
                "xpath"
            )
        self.perform_action(ADDITIONAL_PARAMETERS_XPATH, "click", "xpath")
        self.perform_action(SURFACE_FROM_ID, SURFACE_FROM, "id")
        self.perform_action(SEARCH_BUTTON_XPATH, "click", "xpath")
        self.perform_action(ACCEPT_COOKIES_ID, "click", "id", 4)

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
            self.driver.get(
                "https://docs.google.com/forms/d/e/1FAIpQLSdYR-xloQsQdsHOSE9Kld4MO4OwbbqA7ehE2eDgevfQhe0e"
                            "6w/viewform?usp=sf_link"
            )
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


