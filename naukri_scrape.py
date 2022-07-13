import csv
import os
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

skills_input = "//input[contains(@placeholder, 'Enter skills')]"
experience_input_click = "//div[contains(@class, 'dropdownMainContainer')]"
next_btn = "//a[contains(@class, 'fright fs14 btn-secondary br2')]"
experience_input = "//span[text() ='3 years']"
location_input = "//input[contains(@placeholder, 'Enter location')]"
search_btn = "//div[contains(@class, 'qsbSubmit')]"
jobs_list_article = "//a[contains(@class, 'title fw500 ellipsis')]"

input_name = "IT_salaries"

chrome_options = Options()
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
chrome_options.add_argument("--user-data-dir=naukri")
web_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=chrome_options)
web_driver.get("https://www.naukri.com/")
web_driver.maximize_window()


def naukri_search(web_driver):
    web_driver.find_element(By.XPATH, skills_input).send_keys("Python")
    web_driver.find_element(By.XPATH, experience_input_click).click()
    web_driver.find_element(By.XPATH, experience_input).click()
    web_driver.find_element(By.XPATH, location_input).send_keys("Hyderabad")
    web_driver.find_element(By.XPATH, search_btn).click()


def job_details(web_driver):

    wait_for_page_load(web_driver)
    chwd = web_driver.window_handles[0]
    for j in range(0, 200):
        web_driver.refresh()
        web_driver.implicitly_wait(10)
        time.sleep(2)
        jobs_list = web_driver.find_elements(By.XPATH, jobs_list_article)
        for i in range(len(jobs_list)):
            web_driver.switch_to.window(chwd)
            time.sleep(5)
            print(i)
            url = jobs_list[i].get_attribute("href")
            web_driver.execute_script("window.open(arguments[0], 'new_window')", url)
            switch_to_child_window(web_driver)
            wait_for_page_load(web_driver)
            scraping_data(web_driver)
            web_driver.delete_all_cookies()
            web_driver.close()

        web_driver.switch_to.window(chwd)
        wait_for_page_load(web_driver)
        web_driver.implicitly_wait(10)
        try:
            WebDriverWait(web_driver, 30).until(
                EC.presence_of_element_located((By.XPATH, next_btn)))
            next_button = web_driver.find_element(By.XPATH, next_btn)
            scroll_element_to_view(web_driver, next_btn)
            js_click(web_driver, element=next_button)
            wait_for_page_load(web_driver)
        except Exception:
            os.system('say "your program has finished"')


def scroll_element_to_view(web_driver, elem):
    scroll_element_to_middle = """var viewPortHeight = Math.max(
                                    document.documentElement.clientHeight,
                                    window.innerHeight || 0);
                                                               var elementTop = arguments[
                                                               0].getBoundingClientRect().top;
                                                               window.scrollBy(0, elementTop-(
                                                               viewPortHeight/2));
                                                               """
    WebDriverWait(web_driver, 30).until(
        EC.presence_of_element_located((By.XPATH, elem)))
    next_button = web_driver.find_element(By.XPATH, elem)
    web_driver.execute_script(scroll_element_to_middle, next_button)


def scraping_data(web_driver):
    html_doc = web_driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    try:
        title = soup.find("h1", attrs={"class": 'jd-header-title'})
        job_value = title.string
        job_title = job_value.strip().replace(',', '')
    except Exception:
        job_title = "NA"

    try:
        company_name = soup.find("div", attrs={
            'class': 'jd-header-comp-name'}).text.strip().replace(',', '')
    except Exception:
        company_name = "NA"

    try:
        experience = web_driver.find_element(By.CSS_SELECTOR, "div.exp").text
    except Exception:
        experience = "NA"

    try:
        salary = web_driver.find_element(By.CSS_SELECTOR, "div.salary").text
    except Exception:
        salary = "NA"

    try:
        location = web_driver.find_element(By.CSS_SELECTOR, "div.loc").text
    except Exception:
        location = "NA"

    try:
        key_skills = web_driver.find_element(By.CSS_SELECTOR, "div.key-skill").text
    except Exception:
        key_skills = "NA"

    try:
        about_company = web_driver.find_element(By.CSS_SELECTOR, "section.about-company").text
    except Exception:
        about_company = "NA"

    try:
        job_description = web_driver.find_element(By.CSS_SELECTOR, "div.dang-inner-html").text
        mail_id = re.findall('\S+@\S+', job_description)
        if len(mail_id) > 0:
            for i in range(len(mail_id)):
                job_description = job_description.replace(mail_id[i], "Due to privacy it is "
                                                                      "removed it")

    except Exception:
        job_description = "NA"

    appending_data_to_csv(job_title, company_name, experience, salary, location, key_skills,
                          about_company, job_description)


def appending_data_to_csv(job_title, company_name, experience, salary, location, key_skills,
                          about_company, job_description):
    with open(f'{input_name}.csv', 'a', encoding='utf-8'):
        new_row = [job_title, company_name, experience, salary, location, key_skills,
                   about_company, job_description]
        friend_writer = csv.writer(open(f'{input_name}.csv', 'a', encoding='utf-8'))
        friend_writer.writerow(new_row)


def appending_headers_to_csv():
    with open(f'{input_name}.csv', 'a', encoding='utf-8'):
        headers = ["job_title", "company_name", "experience", "salary", "location", "key_skills",
                   "about_company", "job_descriptio"]
        friend_writer = csv.writer(open(f'{input_name}.csv', 'a', encoding='utf-8'))
        friend_writer.writerow(headers)


def wait_for_page_load(web_driver, timeout=30):
    """
    Waits for document state to be ready.
    :return: none
    """
    try:
        wait = WebDriverWait(web_driver, timeout)
        wait.until(lambda driver: web_driver.execute_script(
            'return document.readyState === "complete"'))
    except Exception:
        print("wait failed")


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


if __name__ == '__main__':
    try:
        naukri_search(web_driver)
        appending_headers_to_csv()
        job_details(web_driver)
    except Exception as ex:
        print(ex)
        web_driver.quit()
