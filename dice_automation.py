import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# ------------------------------ CONFIG ------------------------------
USER_EMAIL = "suryateja233@gmail.com"
USER_PASSWORD = "DevilReturns@006"
SEARCH_KEYWORDS = "aws python"

# ---------------------------- LOCATORS ------------------------------
SELECTORS = {
    "search_input": '#typeaheadInput',
    "search_button": '#submitSearch-button',
    "job_card": '[data-cy="card-title-link"]',
    "apply_button": 'apply-button-wc.hydrated',
    "username_input": '#username.sc-login-form',
    "password_input": '#password.sc-login-form',
    "login_submit": '[data-cy="login-submit"] button',
    "next_button": 'button.btn-next',
    "radio_block": '.radio-input-wrapper',
    "pagination_next": 'li.pagination-next.page-item.ng-star-inserted',
    "iframe_feedback": 'iframe[title="Usabilla Feedback Form"]',
    "iframe_close": '#close_link'
}

# ---------------------------- SETUP BROWSER -------------------------
def init_browser():
    chrome_options = Options()
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "normal"
    chrome_options.add_argument("--disable-features=NetworkService")
    chrome_options.add_argument("--dns-prefetch-disable")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1440,768")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-data-dir=naukri")

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# ---------------------------- MAIN FUNCTION --------------------------
def dice_login(driver):
    dismiss_feedback_iframe(driver)
    search_and_open_first_job(driver)

    for _ in range(300):
        time.sleep(10)
        job_cards = driver.find_elements(By.CSS_SELECTOR, SELECTORS['job_card'])

        for job in job_cards:
            main_window = driver.current_window_handle
            try:
                job.click()
                time.sleep(2)
                switch_to_new_tab(driver, main_window)
                job_info = extract_job_info(driver)
                skill_list = extract_skills(driver)
                write_to_csv(job_info, skill_list)
                apply_to_job(driver)
                handle_authorization_question(driver)
                click_next_button(driver)
                driver.close()
                driver.switch_to.window(main_window)
                time.sleep(5)
            except Exception as ex:
                print(f"Failed: {ex}")
                driver.close()
                driver.switch_to.window(main_window)

        try:
            driver.find_element(By.CSS_SELECTOR, SELECTORS['pagination_next']).click()
        except:
            print("No more pages.")
            break

def write_to_csv(job_data, skills, filename="job_details.csv"):
    # Combine job info and skills
    job_data["Skills"] = ', '.join(skills)
    df = pd.DataFrame([job_data])
    df.to_csv(filename, mode='a', index=False, header=not pd.io.common.file_exists(filename))
    print(f"Saved to {filename}")


def extract_job_info(driver):
    wait = WebDriverWait(driver, 15)

    # 1. Job title
    job_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[data-cy="jobTitle"]'))).text

    # 2. Company
    company = driver.find_element(By.CSS_SELECTOR, '[data-cy="companyNameLink"]').text

    # 3. Location
    location = driver.find_element(By.CSS_SELECTOR, '[data-cy="location"]').text

    # 4. Posted date
    posted = driver.find_element(By.CSS_SELECTOR, '[data-cy="postedDate"] #timeAgo').text

    # 5. Work mode - On Site / Hybrid
    work_modes = driver.find_elements(By.CSS_SELECTOR, '[data-cy="locationDetails"] span[id^="location:"]')
    work_mode_text = ', '.join([w.text for w in work_modes])

    # 6. Pay
    pay = driver.find_element(By.CSS_SELECTOR, 'span[id^="payChip:"]').text

    # 7. Employment Type
    employment_type = driver.find_element(By.CSS_SELECTOR, 'span[id^="employmentDetailChip:"]').text

    return {
        "Job Title": job_title,
        "Company": company,
        "Location": location,
        "Posted/Updated": posted,
        "Work Mode": work_mode_text,
        "Pay": pay,
        "Employment Type": employment_type
    }


def extract_skills(driver):
    # Click on "Show more skills" button if present
    try:
        show_more = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "skillsToggle"))
        )
        show_more.click()
        time.sleep(1)
    except:
        pass  # Button may not always be present

    # Extract skills
    skill_spans = driver.find_elements(By.CSS_SELECTOR, '[data-cy="skillsList"] span[id^="skillChip:"]')
    skills = [s.text for s in skill_spans]
    return skills


# -------------------------- SUPPORT FUNCTIONS ------------------------
def dismiss_feedback_iframe(driver):
    try:
        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS['iframe_feedback'])))
        driver.switch_to.frame(iframe)
        close_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS['iframe_close'])))
        close_btn.click()
        driver.switch_to.default_content()
    except:
        print("No feedback iframe.")


def search_and_open_first_job(driver):
    search_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS['search_input'])))
    search_input.clear()
    search_input.send_keys(SEARCH_KEYWORDS)
    driver.find_element(By.CSS_SELECTOR, SELECTORS['search_button']).click()
    time.sleep(3)


def switch_to_new_tab(driver, current_handle):
    for handle in driver.window_handles:
        if handle != current_handle:
            driver.switch_to.window(handle)
            break


def apply_to_job(driver):
    driver.find_element(By.CSS_SELECTOR, SELECTORS['apply_button']).click()
    try:
        username = driver.find_element(By.CSS_SELECTOR, SELECTORS['username_input'])
        password = driver.find_element(By.CSS_SELECTOR, SELECTORS['password_input'])
        username.send_keys(USER_EMAIL)
        password.send_keys(USER_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, SELECTORS['login_submit']).click()
    except Exception as ex:
        print(f"Already logged in or no login required: {ex}")


def handle_authorization_question(driver):
    try:
        blocks = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, SELECTORS['radio_block'])))
        for block in blocks:
            try:
                question = block.find_element(By.CSS_SELECTOR, "seds-paragraph").text.strip()
                if "authorized to work in the United States" in question:
                    yes_radio = block.find_element(By.XPATH, ".//input[@type='radio' and @value='Yes']")
                    driver.execute_script("arguments[0].click();", yes_radio)
                    print("Clicked 'Yes'")
                    break
            except:
                continue
    except:
        print("No authorization question found")


def click_next_button(driver):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS['next_button']))).click()


if __name__ == '__main__':
    driver = init_browser()
    driver.get("https://www.dice.com/")
    driver.maximize_window()

    try:
        dice_login(driver)
    finally:
        driver.quit()
