import csv
import time
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def switch_to_child_window(driver):
    """
    Switch to child window
    Args:
        driver: webdriver instance
    Returns: None
    """
    p = driver.current_window_handle
    chwd = driver.window_handles
    for w in chwd:
        # switch focus to child window
        if w != p:
            driver.switch_to.window(w)


def save_cookies(accept_cookie=False):

    chrome_options = Options()
    chrome_options.headless = True

    # Driver installation
    if accept_cookie:
        chrome_options.add_argument("--user-data-dir=C:\\Chromecookies")
    web_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                  options=chrome_options)
    web_driver.get("https://www.amazon.in/")
    web_driver.maximize_window()
    web_driver.find_element(By.ID, "twotabsearchtextbox").send_keys("Laptops")
    web_driver.find_element(By.ID, "nav-search-submit-button").click()
    appending_headers_to_csv()

    for j in range(0, 20):
        if j == 20:
            time.sleep(10)
        result = web_driver.find_elements(By.CSS_SELECTOR, "span.a-size-medium.a-color-base."
                                                           "a-text-normal")
        for i in range(len(result)):
            chwd = web_driver.window_handles[0]
            web_driver.switch_to.window(chwd)
            js_click(web_driver, result[i])
            switch_to_child_window(web_driver)
            scraping_data(web_driver)
            web_driver.close()

        chwd = web_driver.window_handles[0]
        web_driver.switch_to.window(chwd)

        time.sleep(5)
        next_button = web_driver.find_element(By.XPATH,
                                              "//a[contains(@aria-label,'Go to next page')]")
        web_driver.execute_script("arguments[0].scrollIntoView();", next_button)
        js_click(web_driver, next_button)
    return web_driver


def scraping_data(web_driver):
    html_doc = web_driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    try:
        title = soup.find("span", attrs={"id": 'productTitle'})
        title_value = title.string
        title_string = title_value.strip().replace(',', '')
    except AttributeError:
        title_string = "NA"

    try:
        price = soup.find("span", attrs={'class': 'apexPriceToPay'}).text.strip().replace(',', '')
    except AttributeError:
        price = "NA"

    # try:
    #     rating = soup.find("i", attrs={
    #         'class': 'a-icon a-icon-star a-star-4-5'}).string.strip().replace(',', '')
    #
    # except AttributeError:
    #     rating = "NA"
    try:
        rating = soup.find(
            "span", attrs={'class': 'a-icon-alt'}).string.strip().replace(',', '')
    except:
        rating = "NA"

    try:
        review_count = soup.find(
            "span", attrs={'id': 'acrCustomerReviewText'}).string.strip().replace(',', '')
    except AttributeError:
        review_count = "NA"

    try:
        available = soup.find("div", attrs={'id': 'availability'})
        available = available.find("span").string.strip().replace(',', '')
    except AttributeError:
        available = "NA"

    appending_data_to_csv(title_string, price, rating, review_count, available)


def wait_for_page_load(self, timeout=30):
    """
    Waits for document state to be ready.
    :return: none
    """
    start_time = datetime.now()
    try:
        wait = WebDriverWait(self.driver, timeout)
        wait.until(lambda driver: self.driver.execute_script(
            'return document.readyState === "complete"'))
    except TimeoutException as te:
        msg = "Exception occurred while loading the page"
        self.log.write_message_error(
            msg, url=self.driver.current_url, start_time=start_time)
        self.log.write_message_exception(te)
        raise te


def js_click(web_driver, element: WebElement = None):
    """
    To find the web element and clicking.
    :param element:  WebElement
    :return: none.
    """
    web_driver.execute_script("arguments[0].click();", element)


def appending_data_to_csv(title_string, price, rating, review_count, available):
    with open('laptops.csv', 'a', encoding='utf-8'):
        new_row = [title_string, price, rating, review_count, available]
        friend_writer = csv.writer(open('laptops.csv', 'a', encoding='utf-8'))
        friend_writer.writerow(new_row)


def appending_headers_to_csv():
    with open('laptops.csv', 'a', encoding='utf-8'):
        headers = ["title_string", "price", "rating", "review_count", "available"]
        friend_writer = csv.writer(open('laptops.csv', 'a', encoding='utf-8'))
        friend_writer.writerow(headers)


if __name__ == '__main__':
    web_driver = save_cookies()
    web_driver.quit()
