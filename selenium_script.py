import datetime
import time
import sys
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

EMAIL = "your-email"
PASSWORD = "your-password"
# TARGET_DAY_NAME must match the day abbreviations used on the website,
# which are in Romanian: "Lu", "Ma", "Mi", "Jo", "Vi", "Sâ", "Du".
# Changing this to English will break the day selection logic.
TARGET_DAY_NAME = "Ma"
TARGET_HOUR = "20:00"
PROFILE = sys.argv[1] if len(sys.argv) > 1 else "/app/profile1"
LOGFILE = sys.argv[2] if len(sys.argv) > 2 else "/app/logs/reservation1.txt"

DAY_MAP = {"Lu": 0, "Ma": 1, "Mi": 2, "Jo": 3, "Vi": 4, "Sâ": 5, "Du": 6}


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
    service = Service("/usr/bin/chromedriver")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"--user-data-dir={PROFILE}")
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://www.calendis.ro/cluj-napoca/baza-sportiva-la-terenuri-1/fotbal-1/s")
        human_delay(2, 1)

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
            return

        # search for slot
        slot_found = False
        deadline = datetime.datetime.now() + datetime.timedelta(minutes=10)

        while datetime.datetime.now() < deadline and not slot_found:
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
                driver.refresh()
                human_delay(2, 1)
                select_target_day(driver, target_date)

        if not slot_found:
            return
        
        try:
            # Attempt to confirm reservation
            wait.until(EC.element_to_be_clickable((By.ID, "submit-appointment"))).click()
            wait.until(EC.element_to_be_clickable((By.ID, "regulations-checkbox"))).click()
            wait.until(EC.element_to_be_clickable((By.ID, "confirm-appointment"))).click()
            print("Reservation confirmed!")
        except TimeoutException:
            print("Reservation not possible, slot may be taken. Script continues...")

    finally:
        driver.quit()


if __name__ == "__main__":
    make_reservation()
