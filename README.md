
# Selenium Reservation Server (Home Assistant Add-On)

## Overview

Selenium Reservation Server is a Home Assistant Add-on that automates booking sports fields on **calendis.ro** using Selenium + Chromium, running inside a Supervisor-managed container.

It supports:
- **Manastur** & **Gheorgheni** sports bases  
- Multiple sports (fotbal, tenis, volei, baschet, squash, popice, pingpong, tenis cu peretele)  
- Input validation with automatic fallback (day, hour, sport, location)  
- Configurable login credentials  
- Token-based authentication  
- IP whitelisting  
- REST-triggered reservations  
- Windows execution for debugging (non-HA)
- Multiple parallel Selenium instances  
- Configurable timeout + instance count from UI  
- Optional delay between instances
- Fully configurable behavior from the Home Assistant Add-on UI, including: target day, target hour, location, sport selection, number of Selenium instances, timeout, email, password, tokens and whitelist.
- Meant to be triggered from a Home Assistant automation, exactly like the examples provided, so that the script starts precisely at the desired time (e.g. 19:53).
- Automatic reservation logic for the target day two weeks ahead: the script continuously checks the selected slot (day & hour) and performs the reservation as soon as the slot becomes available for the date exactly two weeks from the selected weekday.
- For example, if you select Tuesday at 20:00 and you trigger the script on Tuesday at 19:53 through a Home Assistant automation, the script loops and refreshes until the booking for the Tuesday two weeks from now appears (usually around 19:55), and immediately performs the reservation.
- The script continues checking and refreshing for as long as the configured timeout value allows, stopping automatically once the timeout limit is reached.

---

## Features

- Full graphical UI inside Home Assistant  
- Automatic injection of environment variables into Selenium  
- Multi-location support  
- Sport validation per location with fallback to default  
- Day & hour normalization with safe defaults  
- Optional **X-Token** authentication  
- Optional **IP Whitelist**  
- Watchdog support for auto-restart  
- Installer script (`setup.sh`)  
- Up to 10 parallel instances  
- Optional instance delay  

---

# Folder Structure

```
local_selenium_reservation/
 ├── Dockerfile
 ├── server.py
 ├── selenium_script.py
 ├── selenium_script_windows.py
 ├── config.json
 ├── setup.sh
 └── README.md
```

---

# Installation Using setup.sh

### Important Step Before Running setup.sh

Home Assistant blocks file writes to system folders unless **Protection Mode is disabled**.

You must temporarily disable it:

1. Go to:  
   **Settings → Add-ons → Advanced SSH & Web Terminal**
2. Click **Configuration**
3. Turn **Protection mode → OFF**
4. Save
5. Restart the add-on

This allows `setup.sh` to copy files into `/data/addons/local/`.

After the add-on installs successfully and appears in the UI, you can safely **re-enable protection mode**:

- Protection mode **should be turned ON again** after installation for security.

---

### 1. Clone the repository

```
git clone https://github.com/luciancibu/home-assistant-selenium-docker.git
cd home-assistant-selenium-docker
```

### 2. Make installer executable

```
chmod +x setup.sh
```

### 3. Run the installer (see "Installation Using setup.sh" section above)

```
./setup.sh
```

This script will:
- Create `/data/addons/local/local_selenium_reservation/`
- Copy all add-on files
- Apply correct permissions
- Reload Supervisor add-ons
- Restart Supervisor
- Make the add-on appear in Home Assistant UI

### Uninstall (only if you want to remove the add-on)

```
./setup.sh remove
```

---

# Installing from Home Assistant

Home Assistant →  
**Settings → Add-ons → Add-on Store → Local Add-ons → Selenium Reservation Server**

Then click:
- Install  
- Start  
- (Optional) Start on Boot  
- (Recommended) Watchdog

---

# Add-On Configuration (UI Options)

| Key           | Type   | Required | Description                                                                           |
|---------------|--------|----------|---------------------------------------------------------------------------------------|
| `email`       | string | yes      | Calendis login email                                                                  |
| `password`    | string | yes      | Calendis login password                                                               |
| `default_day` | string | yes      | One of `Lu`, `Ma`, `Mi`, `Jo`, `Vi`, `Sâ`, `Du`                                       |
| `default_hour`| string | yes      | HH:MM between `10:00`–`21:00`                                                         |
| `location`    | string | yes      | `Manastur` or `Gheorgheni`                                                            |
| `sport`       | string | yes      | fotbal / tenis / volei / baschet / squash / popice / pingpong / tenis cu peretele     |
| `timeout`     | int    | yes      | Minutes to keep searching                                                             |
| `instances`   | int    | yes      | Number of parallel Selenium instances (1–10)                                          |
| `tokens`      | list   | optional | List of valid X-Token headers                                                         |
| `whitelist`   | list   | optional | Allowed IPs                                                                           |

---

# Token Authentication (Recommended)

If you enable tokens, every `/run` request **must** include a matching header  
`X-Token: <token>`

## 1. Add token in `secrets.yaml`

```
selenium_token: YOUR_SECRET_TOKEN
```

## 2. Reference token in Add-on config

```
tokens:
  - !secret selenium_token
```

## 3. Use token in REST command

```yaml
rest_command:
  run_selenium:
    url: "http://<HA_IP>:5000/run"
    method: GET
    headers:
      X-Token: !secret selenium_token
```

If token missing → `401 Unauthorized`  
If invalid → `401 Unauthorized`

If you want no token:

```
tokens: []
```

---

# IP Whitelist

If whitelist contains IPs, only those can call `/run`.

Example:

```
whitelist:
  - "192.168.xx.xx"
  - "192.168.xx.xx"
```

Empty whitelist disables filtering:

```
whitelist: []
```

---

# API Endpoints

| Endpoint  | Description              |
|-----------|--------------------------|
| `/`       | Status                   |
| `/run`    | Triggers Selenium job    |
| `/health` | Watchdog healthcheck     |

---

# Trigger Selenium Job

### Without token

```
http://<HA_IP>:5000/run
```

### With token

```
curl -H "X-Token: YOUR_TOKEN" http://<HA_IP>:5000/run
```

---

# Home Assistant Integration

## REST Command (with token)

```yaml
rest_command:
  run_selenium:
    url: "http://<HA_IP>:5000/run"
    method: GET
    headers:
      X-Token: !secret selenium_token
```

## REST Command (without token)

```yaml
rest_command:
  run_selenium:
    url: "http://<HA_IP>:5000/run"
    method: GET
```

---

# Example Automation

```yaml
alias: Auto Selenium Reservation
trigger:
  - platform: time
    at: "19:53:00"
condition:
  - condition: time
    weekday:
      - tue
action:
  - service: rest_command.run_selenium
mode: single
```

---

# Viewing Logs

```
ha addons logs local_selenium_reservation -f
```

---

# Windows: Running the Reservation Script Locally

A Windows-compatible script (`selenium_script_windows.py`) allows debugging Selenium outside of Home Assistant.

## 1. Install Google Chrome  
Download:  
https://www.google.com/chrome/

## 2. Check Chrome Version  
Go to:

```
chrome://settings/help
```

Example:
```
Version 142.0.7444.163
```

## 3. Download the Correct ChromeDriver  
Visit:  

https://googlechromelabs.github.io/chrome-for-testing/

Download:
```
chromedriver-win64.zip
```

Version **must** match your installed Chrome.

Extract to:

```
C:\Tools\chromedriver\chromedriver.exe
```

## 4. Install Selenium

```
pip install selenium
```

## 5. Run the script

```
python selenium_script_windows.py
```

A visible Chrome window will open and complete the reservation flow.

---