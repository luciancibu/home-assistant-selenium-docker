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

EMAIL = "email"
PASSWORD = "password"

DAY_MAP = {"Lu": 0, "Ma": 1, "Mi": 2, "Jo": 3, "Vi": 4, "Sâ": 5, "Du": 6}
TARGET_DAY_NAME = "Ma"
TARGET_HOUR = "20:00"
LOCATION = "Manastur"

SPORT_RAW = "Fotbal"


def validator(value, valid_value, default):
    if value is None:
        return default
    value = value.strip()

    if value == "Sa":
        value = "Sâ"

    if value == "":
        return default

    if isinstance(valid_value, dict):
        valid_value = valid_value.keys()

    if value not in valid_value:
        return default

    return value


def hour_validator(value, default):
    if value is None:
        return default

    value = value.strip()
    if value == "":
        return default

    if value.isdigit():
        hour = int(value)
    else:
        if ":" in value:
            hour_str = value.split(":", 1)[0]
            if not hour_str.isdigit():
                return default
            hour = int(hour_str)
        else:
            return default

    if not (10 <= hour <= 21):
        return default

    return f"{hour:02d}:00"


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
        "pingpong": "/cluj-napoca/baza-sportiva-gheorgheni/tenis-de-masa-523/s"
    }
}

TARGET_DAY_NAME = validator(TARGET_DAY_NAME, DAY_MAP, "Ma")
TARGET_HOUR = hour_validator(TARGET_HOUR, "20:00")
LOCATION = validator(LOCATION, LOCATION_URLS, "manastur").lower()

SPORT = validator(SPORT_RAW, SPORT_ALIAS, "fotbal").lower()
SPORT_KEY = SPORT_ALIAS.get(SPORT, "fotbal")

if SPORT_KEY not in SPORT_LINKS[LOCATION]:
    SPORT_KEY = "fotbal"

SPORT_LINK = SPORT_LINKS[LOCATION][SPORT_KEY]
BASE_URL = LOCATION_URLS[LOCATION]


def human_delay(base=1.0, var=0.5):
    delay = base + random.uniform(-var, var)
    if delay < 0:
        delay = 0.2
    time.sleep(delay)


def get_target_date():
    today = datetime.date.today()
    weekday_today = today.weekday()
    target_weekday = DAY_MAP[TARGET_DAY_NAME]

    days_ahead = (target_weekday - weekday_today) % 7
    if days_ahead == 0:
        days_ahead = 7

    return today + datetime.timedelta(days=days_ahead + 7)


def select_target_day(driver, target_date):
    attempts = 0

    while attempts < 5:
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.day"))
            )
        except:
            pass

        days = driver.find_elements(By.CSS_SELECTOR, "div.day")

        for d in days:
            try:
                day_nr = d.find_element(By.CSS_SELECTOR, "div.day-nr").text.strip()
                day_week = d.find_element(By.CSS_SELECTOR, "div.day-week").text.strip()

                if day_nr == str(target_date.day) and day_week == TARGET_DAY_NAME:
                    driver.execute_script("arguments[0].click();", d)
                    return True

            except:
                continue

        driver.execute_script(
            "document.querySelector('.calendar-arrow.right-arrow').click();"
        )
        try:
            WebDriverWait(driver, 3).until_not(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "#appointment-slots"), "Se caută"
                )
            )
        except:
            pass

        attempts += 1

    return False


def make_reservation():
    service = Service(r"C:\tools\chromedriver\chromedriver.exe")

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(BASE_URL)
        #human_delay(1)


        driver.execute_script("window.scrollBy(0, 400);")
        #human_delay(1)
        target_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '{SPORT_LINK}')]"))
        )
        driver.execute_script("arguments[0].click();", target_btn)
        #human_delay(2)

        # cookie
        try:
            wait.until(EC.element_to_be_clickable((By.ID, "cookie-accept"))).click()
        except:
            pass

        # login
        try:
            email_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="E-mail"]'))
            )
            if email_input.is_displayed():
                email_input.clear()
                email_input.send_keys(EMAIL)

                password_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Parolă"]')
                password_input.clear()
                password_input.send_keys(PASSWORD)
                password_input.send_keys(Keys.RETURN)

        except TimeoutException:
            pass

        target_date = get_target_date()
        select_target_day(driver, target_date)

        # search slot
        slot_found = False
        deadline = datetime.datetime.now() + datetime.timedelta(minutes=10)

        while datetime.datetime.now() < deadline and not slot_found:

            slots = driver.find_elements(By.CSS_SELECTOR, "#appointment-slots .slot-item")

            for s in slots:
                try:
                    hour = s.find_element(By.TAG_NAME, "strong").text.strip()
                    if hour == TARGET_HOUR:
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});", s
                        )
                        s.click()
                        slot_found = True
                        break
                except:
                    continue
            if not slot_found:

                driver.execute_script(
                    "document.querySelector('.calendar-arrow.right-arrow').click();"
                )
                try:
                    WebDriverWait(driver, 3).until_not(
                        EC.text_to_be_present_in_element(
                            (By.CSS_SELECTOR, "#appointment-slots"), "Se caută"
                        )
                    )
                except:
                    pass

                driver.execute_script(
                    "document.querySelector('.calendar-arrow.left-arrow').click();"
                )

                try:
                    WebDriverWait(driver, 3).until_not(
                        EC.text_to_be_present_in_element(
                            (By.CSS_SELECTOR, "#appointment-slots"), "Se caută"
                        )
                    )
                except:
                    pass

                select_target_day(driver, target_date)

        if not slot_found:
            return

        # confirmation flow
        wait.until(EC.element_to_be_clickable((By.ID, "submit-appointment"))).click()
        wait.until(EC.element_to_be_clickable((By.ID, "regulations-checkbox"))).click()
        wait.until(EC.element_to_be_clickable((By.ID, "confirm-appointment"))).click()

    finally:
        driver.quit()


if __name__ == "__main__":
    make_reservation()
