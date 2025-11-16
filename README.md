
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
- Installer script (`setup.sh`) for quick deployment  

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

### 1. Clone the repository

```
git clone https://github.com/luciancibu/home-assistant-selenium-docker.git
cd home-assistant-selenium-docker
```

### 2. Make installer executable

```
chmod +x setup.sh
```

### 3. Run the installer

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

### Uninstall

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
| `location`    | string | yes      | `manastur` or `gheorgheni`                                                            |
| `sport`       | string | yes      | fotbal / tenis / volei / baschet / squash / popice / pingpong / tenis cu peretele     |
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
    at: "19:55:00"
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
C:	ools\chromedriver\chromedriver.exe
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