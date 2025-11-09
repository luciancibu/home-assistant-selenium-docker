# Home Assistant Selenium Football Reservation

This project automates football field reservations on [Calendis](https://www.calendis.ro) using Python and Selenium, packaged inside a Docker container. It allows you to automatically reserve football slots for a target day and time, running multiple instances if needed.

---

## Prerequisites

Before running the scripts, make sure you have:

1. **Access to Home Assistant terminal via SSH**  
   - Install the SSH & Web Terminal add-on in Home Assistant.
   - Configure a user and password for SSH access.
   - Ensure you can open a terminal to run commands like `docker` and `bash`.

2. **Docker installed on Home Assistant**  
   - Home Assistant OS includes Docker by default.

   - Verify Docker is working:
```bash
     docker --version
```

## Project Structure

```
home-assistant-selenium-docker/
│
├── Dockerfile            # Dockerfile to build the container with Python, Chrome, and Selenium
├── selenium_script.py    # Main Python script that performs the reservation
├── run.sh                # Bash script to run the Selenium script (single or multiple instances)
```

---

## Files Description

This is the main Python script that:

* Opens Chrome in headless mode.
* Logs in to Calendis using the provided credentials.
* Selects the target day and hour for the reservation.
* Clicks through cookies, login prompts, and reservation confirmations.
* Uses **Romanian day abbreviations**: `"Lu", "Ma", "Mi", "Jo", "Vi", "Sâ", "Du"`.

**Important:** The `TARGET_DAY_NAME` must remain in Romanian. Changing it to English will break the day selection logic.

**Configuration variables:**

```python
EMAIL = "your_email@example.com"
PASSWORD = "your_password"
TARGET_DAY_NAME = "Ma"  # Must be in Romanian
TARGET_HOUR = "20:00"
```

---


## Usage

1. **Build the Docker image:**

```bash
docker build -t selenium_ha .
```

2. **Run the Selenium script:**

```bash
bash ./run.sh &
```

3. **Check if script is running:**
```bash
ps aux | grep run.sh
```

4. **Optional:** Modify `run.sh` to launch multiple instances in parallel.

---

## Notes

* **Day abbreviations must remain in Romanian** for the script to properly select the target day.
* Headless Chrome is used to allow running in environments without a display.

---
