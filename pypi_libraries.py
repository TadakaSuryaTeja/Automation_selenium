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

input_name = "pypi_libraries"


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
    web_driver.get("https://pypi.org/")
    web_driver.maximize_window()
    web_driver.find_element(By.XPATH, "//a[contains(@href, '/search/')]").click()
    web_driver.find_element(By.XPATH, "//button[contains(text(),'Programming Language')]").click()
    web_driver.find_element(By.ID, "Programming_Language_._Python").click()
    appending_headers_to_csv()
    chwd = web_driver.window_handles[0]

    for j in range(0, 1000):
        web_driver.refresh()
        web_driver.implicitly_wait(10)
        time.sleep(2)
        result = web_driver.find_elements(By.XPATH, "//h3[contains(@class,'package-snippet__title')]//parent::a")
        for i in range(len(result)):
            web_driver.switch_to.window(chwd)
            url = result[i].get_attribute("href")
            web_driver.execute_script("window.open(arguments[0], 'new_window')", url)
            switch_to_child_window(web_driver)
            wait_for_page_load(web_driver)
            scraping_data(web_driver)
            web_driver.delete_all_cookies()

            web_driver.close()
        scroll_element_to_middle = """var viewPortHeight = Math.max(
                            document.documentElement.clientHeight,
                            window.innerHeight || 0);
                                                       var elementTop = arguments[
                                                       0].getBoundingClientRect().top;
                                                       window.scrollBy(0, elementTop-(
                                                       viewPortHeight/2));
                                                       """
        web_driver.switch_to.window(chwd)
        wait_for_page_load(web_driver)
        web_driver.implicitly_wait(10)
        try:
            WebDriverWait(web_driver, 30).until(EC.presence_of_element_located((By.XPATH,
                                                                                "//a[contains(text(), 'Next')]")))
            next_button = web_driver.find_element(By.XPATH,
                                                  "//a[contains(text(), 'Next')]")

            web_driver.execute_script(scroll_element_to_middle, next_button)
            js_click(web_driver, element=next_button)
            wait_for_page_load(web_driver)
        except Exception:
                os.system('say "your program has finished"')

    return web_driver


def scraping_data(web_driver):
    # wait_for_page_load(web_driver)
    html_doc = web_driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    try:
        title_string = soup.find("h1", attrs={'class': 'package-header__name'}).text.strip()
    except AttributeError:
        title_string = "NA"

    try:
        installation_cmd = soup.find("span", attrs={
            'id': ['pip-command']}).text.strip()
    except AttributeError:
        installation_cmd = "NA"

    try:
        released_date = soup.find("p", attrs={'class': 'package-header__date'}).text.strip()
    except Exception:
        released_date = "NA"

    try:
        release_tag = soup.find("a", attrs={'class': 'status-badge status-badge--good'}).text.strip()
    except AttributeError:
        release_tag = "NA"

    appending_data_to_csv(title_string, installation_cmd, released_date, release_tag)


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


def appending_data_to_csv(title_string, installation_cmd, released_date, release_tag):
    with open(f'{input_name}.csv', 'a', encoding='utf-8'):
        new_row = [title_string, installation_cmd, released_date, release_tag]
        friend_writer = csv.writer(open(f'{input_name}.csv', 'a', encoding='utf-8'))
        friend_writer.writerow(new_row)


def appending_headers_to_csv():
    with open(f'{input_name}.csv', 'a', encoding='utf-8'):
        headers = ["Package Name", "Installation Command", "released_date", "release_tag"]
        friend_writer = csv.writer(open(f'{input_name}.csv', 'a', encoding='utf-8'))
        friend_writer.writerow(headers)


if __name__ == '__main__':
    web_driver = save_cookies()
    web_driver.quit()
