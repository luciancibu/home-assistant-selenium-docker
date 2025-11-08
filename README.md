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

3. **Optional:** Create directories for Selenium profiles and logs:
```bash
   mkdir -p /config/home-assistant-selenium-docker/logs
   mkdir -p /config/home-assistant-selenium-docker/profile1
   mkdir -p /config/home-assistant-selenium-docker/profile2
   # Repeat for profile3..profile5 if needed


## Project Structure

```
home-assistant-selenium-docker/
│
├── Dockerfile            # Dockerfile to build the container with Python, Chrome, and Selenium
├── selenium_script.py    # Main Python script that performs the reservation
├── run.sh                # Bash script to run the Selenium script (single or multiple profiles)
└── profile1/ ... profile5/  # Optional Selenium browser profiles for session management
```

---

## Files Description

### 1. `selenium_script.py`

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
PROFILE = sys.argv[1] if len(sys.argv) > 1 else "/app/profile1"
LOGFILE = sys.argv[2] if len(sys.argv) > 2 else "/app/logs/reservation1.txt"
```

---

### 2. `Dockerfile`

This Dockerfile sets up the environment to run the Selenium script:

* Base image: `python:3.11-slim`
* Installs Chromium and all required dependencies.
* Installs Selenium Python package.
* Copies the `selenium_script.py` into `/app` inside the container.
* Default command runs the script with a profile and logs.

**Build Docker image:**

```bash
docker build -t selenium_ha .
```

---

### 3. `run.sh`

Bash script to run the Selenium script inside Docker. It can be modified to run multiple profiles if needed.

**Notes:**

* Maps host directories for profiles and logs into the container.
* Ensures persistent login sessions with separate profiles.
* Multiple containers can run in parallel using different profiles.

---

### 4. Profiles

`profile1/` ... `profile5/` are optional directories to store Selenium browser session data (cookies, local storage). Using profiles allows maintaining login sessions across script runs without re-entering credentials.

---

## Usage

1. **Build the Docker image:**

```bash
docker build -t selenium_ha .
```

2. **Run the Selenium script with a profile:**

```bash
bash ./run.sh &
```

3. **Check if script is running:**
```bash
ps aux | grep run.sh
```

4. **Optional:** Modify `run.sh` to run multiple profiles at once for parallel reservations.

---

## Notes

* **Day abbreviations must remain in Romanian** for the script to properly select the target day.
* Logs are written inside `/app/logs` inside the container.
* Headless Chrome is used to allow running in environments without a display.
* Ensure `/path/to/profile` directories exist and are writable for session persistence.

---
