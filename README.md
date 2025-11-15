# Selenium Reservation Server (Home Assistant Add-on)

## Overview

Selenium Reservation Server is a Home Assistant Add-on that automates
booking sports fields on calendis.ro using Selenium + Chromium running
inside a Supervisor-managed container.

The add-on allows: - configuration of **email**, **password**, **day**,
**hour** - optional **X-Token authentication** - optional **IP
whitelist** - triggering via REST or HA Automations - safe isolation
within HA OS

------------------------------------------------------------------------

# Features

-   Full UI configuration
-   Environment variables passed automatically into Selenium
-   Optional security (tokens + IP whitelist)
-   Watchdog health endpoint
-   Can be triggered manually or via automations
-   Auto-install via `setup.sh`

------------------------------------------------------------------------

# Folder Structure

    local_selenium_reservation/
     ├── Dockerfile
     ├── server.py
     ├── selenium_script.py
     └── config.json

------------------------------------------------------------------------

# Automatic Installation (setup.sh)

This repository includes a **setup.sh** script that automatically
installs the add-on into Home Assistant Supervisor.

### Installation Steps

### 1. Clone the repository

    git https://github.com/luciancibu/home-assistant-selenium-docker.git
    cd home-assistant-selenium-docker

### 2. Make the installer executable

    chmod +x setup.sh

### 3. Install the Add-on

    ./setup.sh

What this script does: - creates
`/data/addons/local/local_selenium_reservation/` inside Supervisor -
copies Dockerfile, server.py, selenium_script.py, config.json - sets
correct permissions - reloads local add-ons - restarts Supervisor -
makes the add-on appear in HA UI

### Uninstallation

    ./setup.sh remove

This will: - stop the add-on - uninstall it - remove old folders -
restart Supervisor

------------------------------------------------------------------------

# Installing from Home Assistant UI

After running `setup.sh`, the add-on will show up inside Home Assistant.

Go to:

Home Assistant →  
**Settings → Add-ons → Add-on Store → Local Add-ons → Selenium Reservation Server**

Then:

- Click **Install**
- Click **Start**
- (Optional) Enable **Start on boot**
- (Recommended) Enable **Watchdog**, so Home Assistant can automatically restart the add-on if something crashes

------------------------------------------------------------------------

# Add-on Configuration (UI Options)

  ----------------------------------------------------------------------------
  Key                       Type        Required       Description
  ------------------------- ----------- -------------- -----------------------
  `email`                   string      yes            Calendis login email

  `password`                string      yes            Calendis login password

  `default_day`             string      yes            One of: `Lu`, `Ma`,
                                                       `Mi`, `Jo`, `Vi`, `Sâ`,
                                                       `Du`

  `default_hour`            string      yes            Format HH:MM,
                                                       e.g. `08:00`--`21:00`

  `tokens`                  list        optional       List of valid tokens.
                                                       Empty = token disabled

  `whitelist`               list        optional       IP whitelist. Empty =
                                                       all IPs allowed
  ----------------------------------------------------------------------------

### Token optional

If `tokens: []`, `/run` works without a token.

### Whitelist optional

If `whitelist: []`, all IPs can call `/run`.

------------------------------------------------------------------------

# API Endpoints

  Endpoint    Description
  ----------- ----------------------
  `/`         Status page
  `/run`      Starts Selenium job
  `/health`   Watchdog healthcheck

------------------------------------------------------------------------

# Triggering Selenium manually

    http://<HOME_ASSISTANT_IP>:5000/run

(If tokens are enabled, send header: `X-Token: <value>`)

------------------------------------------------------------------------

# Home Assistant Integration

## 1️ **REST Command (with token authentication)**

### Add token to `secrets.yaml`:

    selenium_token: YOUR_SECRET_TOKEN

### Add rest_command:

``` yaml
rest_command:
  run_selenium:
    url: "http://<HOME_ASSISTANT_IP>:5000/run"
    method: GET
    headers:
      X-Token: !secret selenium_token
```

------------------------------------------------------------------------

## 2️ **REST Command (without token)**

``` yaml
rest_command:
  run_selenium:
    url: "http://<HOME_ASSISTANT_IP>:5000/run"
    method: GET
```

------------------------------------------------------------------------

# Example Automation

### With/Without token:

``` yaml
alias: Secure Selenium Reservation
trigger:
  - platform: time
    at: "19:55:00"
action:
  - service: rest_command.run_selenium
mode: single
```

------------------------------------------------------------------------

# Health Check

Supervisor monitors:

    http://[HOST]:5000/health

If down → container auto-restarts.

------------------------------------------------------------------------

# Debugging

### View logs:

    ha addons logs local_selenium_reservation -f
