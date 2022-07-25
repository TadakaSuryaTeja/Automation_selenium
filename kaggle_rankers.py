import csv
import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

# from webdriver_manager.firefox import GeckoDriverManager

input_name = "kaggle_competitions"


def wait_for_page_load(web_driver, timeout=30):
    """
    Waits for document state to be ready.
    :return: none
    """
    wait = WebDriverWait(web_driver, timeout)
    wait.until(lambda driver: web_driver.execute_script(
            'return document.readyState === "complete"'))


def js_click(web_driver, element: WebElement = None):
    """
    To find the web element and clicking.
    :param element:  WebElement
    :return: none.
    """
    web_driver.execute_script("arguments[0].click();", element)


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
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "normal"
    # chrome_options.headless = True
    chrome_options.add_argument("--disable-features=NetworkService")
    chrome_options.add_argument("--dns-prefetch-disable")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1440,768")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")
    # profile = webdriver.FirefoxProfile()
    # profile.set_preference("browser.cache.disk.enable", False)
    # profile.set_preference("browser.cache.memory.enable", False)
    # profile.set_preference("browser.cache.offline.enable", False)
    # profile.set_preference("network.http.use-cache", False)
    # Driver installation
    # if accept_cookie:
    #     chrome_options.add_argument("--user-data-dir=C:\\Chromecookies")
    web_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                  chrome_options=chrome_options)
    web_driver.get("https://www.kaggle.com/rankings")
    web_driver.maximize_window()
    appending_headers_to_csv()
    chwd = web_driver.window_handles[0]
    scroll_to_infinite_bottom(web_driver)
    result = web_driver.find_elements(By.XPATH, "//div[contains(@class,'leaderboards__name')]//child::a")
    for i in range(1000):
        web_driver.switch_to.window(chwd)
        url = result[i].get_attribute("href")
        web_driver.execute_script("window.open(arguments[0], 'new_window')", url)
        wait_for_page_load(web_driver)
        switch_to_child_window(web_driver)
        wait_for_page_load(web_driver)
        WebDriverWait(web_driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "profile__head-display-name")))
        scraping_data(web_driver)
        web_driver.delete_all_cookies()
        web_driver.close()

    return web_driver


def scroll_to_infinite_bottom(driver):
    from selenium.webdriver.common.keys import Keys

    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)


def scraping_data(web_driver):
    # wait_for_page_load(web_driver)
    html_doc = web_driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    try:
        name = soup.find("span", attrs={'class': 'profile__head-display-name'}).text.strip()
    except AttributeError:
        name = "NA"

    try:
        occupation = soup.find("p", attrs={'class': 'profile__user-occupation'}).text.strip()
    except Exception:
        occupation = "NA"

    try:
        progression = soup.find("a", attrs={'title': 'Progression'}).text.strip()
    except Exception:
        progression = "NA"

    try:
        competitions = soup.find("a", attrs={'title': 'competitions'}).text.strip()
    except Exception:
        competitions = "NA"

    try:
        datasets = soup.find("a", attrs={'title': 'datasets'}).text.strip()
    except Exception:
        datasets = "NA"

    try:
        code = soup.find("a", attrs={'title': 'code'}).text.strip()
    except Exception:
        code = "NA"

    try:
        discussion = soup.find("a", attrs={'title': 'discussion'}).text.strip()
    except Exception:
        discussion = "NA"

    try:
        competitions_title = soup.find("span", attrs={'class': 'achievement-summary__title '
                                                               'achievement-summary__title--link'}).text.strip()
    except Exception:
        competitions_title = "NA"

    try:
        competitions_rank = soup.find("div", attrs={'class': 'achievement-summary__rank-box'}).text.strip()
    except Exception:
        competitions_rank = "NA"

    try:
        gold_rank = soup.find("div", attrs={'class': 'achievement-summary__medal achievement-summary__medal--gold '
                                                     'achievement-summary__medal--highlights'}).text.strip()
    except Exception:
        gold_rank = "NA"

    try:
        silver_rank = soup.find("div", attrs={'class': 'achievement-summary__medal achievement-summary__medal--silver '
                                                       'achievement-summary__medal--highlights'}).text.strip()
    except Exception:
        silver_rank = "NA"

    try:
        bronze_rank = soup.find("div", attrs={'class': 'achievement-summary__medal achievement-summary__medal--bronze '
                                                       'achievement-summary__medal--highlights'}).text.strip()
    except Exception:
        bronze_rank = "NA"

    appending_data_to_csv(name, occupation, progression, competitions, datasets, code, discussion,
                          competitions_title, competitions_rank, gold_rank, silver_rank, bronze_rank)


def wait_for_all_images_to_load(web_driver):
    """
        To wait for all images in the page to load
        :param timeout: wait time
        """
    scroll_element_to_middle = """var viewPortHeight = Math.max(
        document.documentElement.clientHeight,
                                   window.innerHeight || 0);
                                                              var elementTop = arguments[
                                                              0].getBoundingClientRect().top;
                                                              window.scrollBy(0, elementTop-(
                                                              viewPortHeight/2));"""
    all_images = web_driver.find_elements(By.TAG_NAME, 'img')
    for each_ele in all_images:
        web_driver.execute_script(scroll_element_to_middle, each_ele)
        wait = WebDriverWait(web_driver, 20)
        if 'visibility: hidden' not in each_ele.get_attribute('style'):
            wait.until(lambda driver: driver.execute_script(
                    "return arguments[0].complete && typeof arguments[0].naturalWidth != "
                    "\"undefined\"\n"
                    " && arguments[0].naturalWidth > 0", each_ele))

    web_driver.execute_script("window.scrollTo(0, 0);")


def appending_data_to_csv(name, occupation, progression, competitions, datasets, code, discussion,
                          competitions_title, competitions_rank, gold_rank, silver_rank, bronze_rank):
    with open(f'{input_name}.csv', 'a', encoding='utf-8'):
        new_row = [name, occupation, progression, competitions, datasets, code, discussion,
                   competitions_title, competitions_rank, gold_rank, silver_rank, bronze_rank]
        friend_writer = csv.writer(open(f'{input_name}.csv', 'a', encoding='utf-8'))
        friend_writer.writerow(new_row)


def appending_headers_to_csv():
    with open(f'{input_name}.csv', 'a', encoding='utf-8'):
        headers = ["name", "occupation", "progression", "competitions", "datasets", "code", "discussion",
                   "competitions_title", "competitions_rank", "gold_rank", "silver_rank", "bronze_rank"]
        friend_writer = csv.writer(open(f'{input_name}.csv', 'a', encoding='utf-8'))
        friend_writer.writerow(headers)


if __name__ == '__main__':
    web_driver = save_cookies()
    web_driver.quit()
