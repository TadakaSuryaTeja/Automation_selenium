import csv
import getpass
import logging
import os
import time

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui
from webdriver_manager.chrome import ChromeDriverManager

# Variable Declaration
sign_in_btn = 'a.nav__button-secondary'
username_input = 'username'
password_input = 'password'
submit_btn = '.btn__primary--large'
jobs_btn = 'ember19'
job_search_by_skill_btn = "//input[contains(@id, 'jobs-search-box-keyword')]"
job_search_place = "//input[contains(@id, 'jobs-search-box-location')]"
job_card_container = "jobs-search-results__list-item"
apply_btn = "//div[@class='mt5']//span[text()='Easy Apply']"
next_btn = '//span[text()="Next"]'
submit_application_btn = "//button[contains(@aria-label, 'Submit application')]"
job_description_container = ".jobs-description.jobs-description--reformatted"
remove_resume_btn = "//button[contains(@aria-label,'Remove uploaded document')]"


def save_cookies(accept_cookie):
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=C:\\Chromecookies")

    # Driver installation
    if accept_cookie:
        web_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    else:
        web_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    web_driver.get("https://in.linkedin.com/")
    web_driver.maximize_window()
    return web_driver


def linkedin_login(web_driver):
    if validating_locator_availability(web_driver, By.CSS_SELECTOR, sign_in_btn):
        username_txt = input("Enter the Username")
        password_txt = getpass.getpass("Enter your password: ")
        web_driver.find_element(By.ID, username_input).send_keys(username_txt)
        web_driver.find_element(By.ID, password_input).send_keys(password_txt)
        web_driver.find_element(By.CSS_SELECTOR, submit_btn).click()


def job_search(web_driver):
    skill_txt = input(str("Enter the skill to search: "))
    place_txt = input(str("Enter the preferred location: "))
    web_driver.find_element(By.ID, jobs_btn).click()
    time.sleep(5)
    job_search_input = web_driver.find_element(By.XPATH, job_search_by_skill_btn)
    job_search_input.click()
    job_search_input.send_keys(skill_txt)
    time.sleep(2)
    job_search_input.send_keys(Keys.ENTER)
    time.sleep(5)
    job_place_input = web_driver.find_element(By.XPATH, job_search_place)
    job_place_input.click()
    job_place_input.clear()
    job_place_input.send_keys(place_txt)
    time.sleep(2)
    job_place_input.send_keys(Keys.ENTER)
    time.sleep(5)


def applying_for_job(web_driver, modify_resume_bool):
    job_title = ""
    job_description = ""
    job_applied_status = False
    result_set = []
    try:
        time.sleep(5)
        job_cards = web_driver.find_elements(By.CLASS_NAME, job_card_container)
        for job in job_cards:
            time.sleep(5)
            job_title = job.text
            job.click()
            job_description_ele = web_driver.find_element(By.CSS_SELECTOR, job_description_container)
            job_description = job_description_ele.text
            try:
                time.sleep(5)
                web_driver.find_element(By.XPATH, apply_btn).click()
            except Exception as e:
                appending_data_to_csv(job_title, job_description, job_applied_status)
                logging.warning(f"Apply button not found {e}")
                continue
            time.sleep(5)
            submit_app = validating_locator_availability(web_driver, By.XPATH, submit_application_btn)
            if not submit_app:
                web_driver.find_element(By.XPATH, next_btn).click()
                if modify_resume_bool:
                    web_driver.find_element(By.XPATH, remove_resume_btn).click()
                    web_driver.find_element(By.CLASS_NAME, "jobs-document-upload__upload-button").click()
                web_driver.find_element(By.XPATH, '//button[contains(@aria-label,"Review")]').click()
                additional_questions = web_driver.find_element(By.XPATH, '//h3[contains(@class,"t-16 t-bold")]')
                if additional_questions:
                    print("User need to enter the answers manually")
                    driver.execute_script("alert('Enter the answers Manually and do not Click Enter')")
                user_name = web_driver.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__title.ember-view").text
                assert "Surya Teja Tadaka" in user_name
                web_elements_review = web_driver.find_elements(By.CSS_SELECTOR, "div.t-14.white-space-pre-line")
                for i in web_elements_review:
                    result = i.text
                    result_set.append(result)
                web_driver.find_element(By.XPATH, "//button[contains(@aria-label,'Submit')]").click()
                assert "suryateja233@gmail.com" in result_set
                assert "9494719275" in result_set
                assert "India (+91)" in result_set
            job_applied_status = True
            close_assessment = web_driver.find_element(By.XPATH, "//button[contains(@class, 'artdeco-modal__dismiss')]")
            if close_assessment:
                time.sleep(5)
                close_assessment.click()

    except Exception as e:
        logging.warning(f"Failed while applying to jobs {e}")
    finally:
        appending_data_to_csv(job_title, job_description, job_applied_status)


def validating_locator_availability(web_driver, locator_type, locator_value):
    submit_app = False
    try:
        submit_app = web_driver.find_element(locator_type, locator_value)
        submit_app.click()
        submit_app = True
    except Exception:
        logging.warning("Locator not found")
    return submit_app


def appending_data_to_csv(job_title, job_description, job_applied_status):
    with open('linkedin.csv', 'a', encoding='utf-8'):
        new_row = [job_title, job_description, job_applied_status]
        friend_writer = csv.writer(open('linkedin.csv', 'a', encoding='utf-8'))
    friend_writer.writerow(new_row)


if __name__ == '__main__':
    # try:
    cookie = False
    driver = save_cookies(accept_cookie=cookie)
    linkedin_login(driver)
    job_search(driver)
    modify_resume = False
    applying_for_job(driver, modify_resume)
    # driver.quit()
# except Exception as ex:
#     driver.quit()
