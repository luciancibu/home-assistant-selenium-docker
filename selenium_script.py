import datetime
import time
import sys
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
DAY_MAP = {"Lu": 0, "Ma": 1, "Mi": 2, "Jo": 3, "Vi": 4, "Sâ": 5, "Du": 6}
TIMEOUT = int(os.getenv("TIMEOUT") or 10)
TARGET_DAY_NAME = os.getenv("TARGET_DAY_NAME")
TARGET_HOUR = os.getenv("TARGET_HOUR")
LOCATION = os.getenv("LOCATION").lower()
SPORT = os.getenv("SPORT").lower()

LOCATION_URLS = {
    "manastur": "https://www.calendis.ro/cluj-napoca/baza-sportiva-la-terenuri-1/b",
    "gheorgheni": "https://www.calendis.ro/cluj-napoca/baza-sportiva-gheorgheni/b"
}

SPORT_ALIAS = {
    "fotbal": "fotbal",
    "baschet": "baschet",
    "squash": "squash",
    "tenis": "tenis",
    "tenis cu peretele": "tenis_perete",
    "tenis de masa": "pingpong",
    "pingpong": "pingpong",
    "volei": "volei",
    "popice": "popice"
}

SPORT_LINKS = {
    "manastur": {
        "fotbal": "/cluj-napoca/baza-sportiva-la-terenuri-1/fotbal-1/24478/s",
        "baschet": "/cluj-napoca/baza-sportiva-la-terenuri-1/baschet-1/24477/s",
        "squash": "/cluj-napoca/baza-sportiva-la-terenuri-1/squash/24479/s",
        "tenis": "/cluj-napoca/baza-sportiva-la-terenuri-1/tenis-1/24480/s",
        "tenis_perete": "/cluj-napoca/baza-sportiva-la-terenuri-1/tenis-cu-peretele-1/24481/s",
        "pingpong": "/cluj-napoca/baza-sportiva-la-terenuri-1/tenis-de-masa-1/24482/s",
        "volei": "/cluj-napoca/baza-sportiva-la-terenuri-1/volei/24483/s"
    },
    "gheorgheni": {
        "fotbal": "/cluj-napoca/baza-sportiva-gheorgheni/fotbal/513/s",
        "baschet": "/cluj-napoca/baza-sportiva-gheorgheni/baschet/515/s",
        "popice": "/cluj-napoca/baza-sportiva-gheorgheni/popice/521/s",
        "tenis": "/cluj-napoca/baza-sportiva-gheorgheni/tenis/511/s",
        "tenis_perete": "/cluj-napoca/baza-sportiva-gheorgheni/tenis-cu-peretele/519/s",
        "pingpong": "/cluj-napoca/baza-sportiva-gheorgheni/tenis-de-masa/523/s"
    }
}

SPORT_KEY = SPORT_ALIAS.get(SPORT)

SPORT_LINK = SPORT_LINKS[LOCATION][SPORT_KEY]
BASE_URL = LOCATION_URLS[LOCATION]


def human_delay(base=1.0, var=0.5):
    delay = base + random.uniform(-var, var)
    if delay < 0: delay = 0.2
    time.sleep(delay)

def get_target_date():
    today = datetime.date.today()
    weekday_today = today.weekday()
    target_weekday = DAY_MAP[TARGET_DAY_NAME]
    days_ahead = (target_weekday - weekday_today) % 7
    if days_ahead == 0:
        days_ahead = 7
    target = today + datetime.timedelta(days=days_ahead + 7)
    return target


def select_target_day(driver, target_date):
    attempts = 0
    while attempts < 5:
        days = driver.find_elements(By.CSS_SELECTOR, "div.day")
        for d in days:
            try:
                day_nr = d.find_element(By.CSS_SELECTOR, "div.day-nr").text.strip()
                day_week = d.find_element(By.CSS_SELECTOR, "div.day-week").text.strip()
                if day_nr == str(target_date.day) and day_week == TARGET_DAY_NAME:
                    d.click()
                    human_delay(1, 0.5)
                    return True
            except:
                continue
        driver.execute_script("document.querySelector('.calendar-arrow.right-arrow').click();")
        human_delay(1, 0.5)
        attempts += 1
    return False


def make_reservation():
    FLAG_PATH = "/tmp/reservation_done"

    service = Service("/usr/bin/chromedriver")
    profile = os.getenv("SELENIUM_PROFILE", "/tmp/default-profile")
    options = webdriver.ChromeOptions()
    
    options.add_argument(f"--user-data-dir={profile}")    
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(BASE_URL)
        human_delay(2, 1)

        driver.execute_script("window.scrollBy(0, 400);")
        human_delay(1)

        target_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//a[contains(@href, '{SPORT_LINK}')]")
            )
        )        

        driver.execute_script("arguments[0].click();", target_btn)
        human_delay(2)

        # cookies
        try:
            cookie_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "cookie-accept"))
            )
            cookie_btn.click()
        except:
            pass

        # login
        try:
            email_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="E-mail"]'))
            )
            if email_input.is_displayed():
                email_input.clear()
                for c in EMAIL:
                    email_input.send_keys(c)
                    human_delay(0.1, 0.05)
                password_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Parolă"]')
                password_input.clear()
                for c in PASSWORD:
                    password_input.send_keys(c)
                    human_delay(0.1, 0.05)
                password_input.send_keys(Keys.RETURN)
                human_delay(2, 1)
        except TimeoutException:
            pass

        # target day
        target_date = get_target_date()
        if not select_target_day(driver, target_date):
            driver.refresh()
            
        # search for slot
        slot_found = False
        deadline = datetime.datetime.now() + datetime.timedelta(minutes=TIMEOUT)

        while datetime.datetime.now() < deadline and not slot_found:
            if os.path.exists(FLAG_PATH):
                print("Another instance already completed the reservation. Exiting...")
                driver.quit()
                sys.exit(0)
            slots = driver.find_elements(By.CSS_SELECTOR, "#appointment-slots .slot-item")
            for s in slots:
                try:
                    hour = s.find_element(By.TAG_NAME, "strong").text.strip()
                    if hour == TARGET_HOUR:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", s)
                        human_delay(0.5, 0.2)
                        s.click()
                        slot_found = True
                        human_delay(1, 0.5)
                        break
                except:
                    continue
            if not slot_found:
                human_delay(2, 1)
                
                driver.execute_script(
                    "document.querySelector('.calendar-arrow.right-arrow').click();"
                )
                human_delay(2, 1)
                driver.execute_script(
                    "document.querySelector('.calendar-arrow.left-arrow').click();"
                )
                select_target_day(driver, target_date)               

        if not slot_found:
            return
        
        try:
            # Attempt to confirm reservation
            wait.until(EC.element_to_be_clickable((By.ID, "submit-appointment"))).click()
            wait.until(EC.element_to_be_clickable((By.ID, "regulations-checkbox"))).click()
            wait.until(EC.element_to_be_clickable((By.ID, "confirm-appointment"))).click()
            open(FLAG_PATH, "w").write("done")
            print("Reservation confirmed, flag file created!")
        except TimeoutException:
            print("Reservation not possible, slot may be taken. Script continues...")

    finally:
        driver.quit()


if __name__ == "__main__":
    make_reservation()
