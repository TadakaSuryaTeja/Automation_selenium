import time

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
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
web_driver.get("https://www.dice.com/")
web_driver.maximize_window()


def dice_loging(web_driver):
    switch_to_iframe_cache(web_driver)
    search_input = WebDriverWait(web_driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#typeaheadInput'))
    )
    search_input.clear()
    search_input.send_keys('python')
    web_driver.find_element(By.CSS_SELECTOR, '#submitSearch-button').click()
    web_driver.implicitly_wait(10)
    main_window_handle = web_driver.current_window_handle
    for i in range(3):
        list_of_jobs = web_driver.find_elements(By.CSS_SELECTOR, '[data-cy="card-title-link"]')
        for jobs in list_of_jobs:
            try:
                jobs.click()
                time.sleep(2)

                # Switch to the new tab
                new_window_handle = [handle for handle in web_driver.window_handles if handle != main_window_handle][0]
                web_driver.switch_to.window(new_window_handle)
                web_driver.find_element(By.CSS_SELECTOR, 'apply-button-wc.hydrated').click()
                try:
                    username = web_driver.find_element(By.CSS_SELECTOR, '#username.sc-login-form')
                    password = web_driver.find_element(By.CSS_SELECTOR, '#password.sc-login-form')
                    if username:
                        web_driver.execute_script("arguments[0].scrollIntoView(true);", username)
                        username.send_keys("suryateja233@gmail.com")
                    if password:
                        web_driver.execute_script("arguments[0].scrollIntoView(true);", password)
                        password.send_keys("")
                    WebDriverWait(web_driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="login-submit"] button'))
                    ).click()
                except Exception as ex:
                    print(f"Already Logged in {ex}")
                WebDriverWait(web_driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn-next'))
                ).click()
                try:
                    wait = WebDriverWait(web_driver, 10)
                    # Locate all the question containers
                    radio_blocks = wait.until(EC.presence_of_all_elements_located((
                        By.CSS_SELECTOR, ".radio-input-wrapper"
                    )))

                    for block in radio_blocks:
                        try:
                            # Find the label/question text in this block
                            question_element = block.find_element(By.CSS_SELECTOR, "seds-paragraph")
                            question_text = question_element.text.strip()

                            # If the question matches exactly, click "Yes"
                            if "authorized to work in the United States" in question_text:
                                yes_input = block.find_element(By.XPATH, ".//input[@type='radio' and @value='Yes']")
                                web_driver.execute_script("arguments[0].click();", yes_input)  # Safe JS click

                                print("Clicked 'Yes' for authorization question.")
                                break  # Exit after clicking
                        except Exception as e:
                            print(f"Skipping block due to error: {e}")
                except Exception as ex:
                    print(f"No Question {ex}")
                WebDriverWait(web_driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn-next'))
                ).click()
                web_driver.close()
                web_driver.switch_to.window(main_window_handle)
                time.sleep(5)
            except Exception as ex:
                web_driver.close()
                web_driver.switch_to.window(main_window_handle)
                time.sleep(5)
                print(f"failed{ex}{jobs}")
        web_driver.find_element(By.CSS_SELECTOR, 'li.pagination-next.page-item.ng-star-inserted').click()


def switch_to_iframe_cache(driver):
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[title="Usabilla Feedback Form"]'))
    )
    driver.switch_to.frame(iframe)

    # Now find and click the cancel button (assuming the cancel button has id 'close_link')
    cancel_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#close_link'))
    )
    cancel_button.click()

    # Switch back to the main content if needed
    driver.switch_to.default_content()


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
        dice_loging(web_driver)
    except Exception as ex:
        print(ex)
        web_driver.quit()
