from selenium import webdriver
from time import sleep
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from my_selectors import *

WAIT_TIME_FOR_ELEMENT_TO_LOAD = 3
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

    def perform_action(self, selector_name, action, selector_type, wait_time=WAIT_TIME_FOR_ELEMENT_TO_LOAD):
        """
        waits and locates element, then performs desired action
        :param selector_name: it can be full xpath or name of id
        :param action: click or values for action send_keys
        :param selector_type: id or xpath
        :param wait_time: by default is 3s
        """
        if action == "click":
            if selector_type == "id":
                try:
                    WebDriverWait(self.driver, wait_time).until(
                        EC.element_to_be_clickable((By.ID, selector_name))).click()
                except TimeoutException:
                    print(f"{selector_name} element not loaded")
                except ElementClickInterceptedException:
                    print(f"{selector_name} element raised ElementClickInterceptedException")
            elif selector_type == "xpath":
                try:
                    WebDriverWait(self.driver, wait_time).until(
                        EC.element_to_be_clickable((By.XPATH, selector_name))).click()
                except TimeoutException:
                    print(f"{selector_name} element not loaded")
                except ElementClickInterceptedException:
                    print(f"{selector_name} element raised ElementClickInterceptedException")
            elif selector_type == "css":
                try:
                    WebDriverWait(self.driver, wait_time).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector_name))).click()
                except TimeoutException:
                    print(f"{selector_name} element not loaded")
                except ElementClickInterceptedException:
                    print(f"{selector_name} element raised ElementClickInterceptedException")
        else:
            if selector_type == "id":
                try:
                    WebDriverWait(self.driver, wait_time).until(
                        EC.presence_of_element_located((By.ID, selector_name))).send_keys(action)
                except TimeoutException:
                    print(f"{selector_name} element not loaded")
                except ElementClickInterceptedException:
                    print(f"{selector_name} element raised ElementClickInterceptedException")
            elif selector_type == "xpath":
                print("searching with xpath")
                try:
                    WebDriverWait(self.driver, wait_time).until(
                        EC.presence_of_element_located((By.XPATH, selector_name))).send_keys(action)
                except TimeoutException:
                    print(f"{selector_name} element not loaded")
                except ElementClickInterceptedException:
                    print(f"{selector_name} element raised ElementClickInterceptedException")

    def start_searching(self):
        """
        manages whole process
        """
        self.driver.get("https://www.bezrealitky.cz/")
        self.apply_filters()
        self.read_all_offers()
        self.download_html()

    def close_advertisement(self):
        """
        closes advertisement banner
        """
        advertisement = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[11]/div/div/div[2]/div/a/img")))
        self.driver.execute_script("arguments[0].click();", advertisement)

    def apply_filters(self):
        """
        applies all desired filters
        """
        self.perform_action(TYPE_PRONAJEM_ID, "click", "id")
        self.perform_action(TYPE_BYT_ID, "click", "id")
        self.perform_action(LOCATION_INPUT_ID, "click", "id")
        self.perform_action(TYPE_PRONAJEM_ID, "click", "id")
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
        """
        scrolls through all offers
        """
        are_next_offers = True
        while are_next_offers:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            sleep(1)
            try:
                self.driver.find_element_by_css_selector(NEXT_OFFERS_BUTTON_XPATH).click()
            except NoSuchElementException:
                are_next_offers = False
            sleep(1)

    def download_html(self):
        """
        downloads html with all offers and put each address, price and url link in lists
        """
        html_content = self.driver.find_element_by_xpath(HTML_CONTENT_XPATH).get_attribute('outerHTML')
        soup = BeautifulSoup(html_content, "html.parser")
        articles = soup.find_all(name="a", class_="product__link")
        prices = soup.find_all(name="strong", class_="product__value")

        all_links = [link.get("href") for link in articles]
        all_addresses = [address.getText() for address in articles]
        all_prices = [price.getText() for price in prices]

        self.send_data(addresses=all_addresses, prices=all_prices, links=all_links)

    def send_data(self, addresses, prices, links):
        """
        submits all apartments in google forms
        :param addresses: list of all addresses
        :param prices: list of all prices
        :param links: list of all url links
        """
        for index in range(0, len(addresses)):
            self.driver.get(
                "https://docs.google.com/forms/d/e/1FAIpQLSdYR-xloQsQdsHOSE9Kld4MO4OwbbqA7ehE2eDgevfQhe0e"
                            "6w/viewform?usp=sf_link"
            )
            self.perform_action(ADDRESS_XPATH, addresses[index], "xpath")
            self.perform_action(PRICES_XPATH, prices[index], "xpath")
            self.perform_action(URL_XPATH, links[index], "xpath")
            self.perform_action(SUBMIT_XPATH, "click", "xpath")


