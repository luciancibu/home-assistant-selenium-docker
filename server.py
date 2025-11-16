from flask import Flask, request
import subprocess
import os
import json

app = Flask(__name__)

with open("/data/options.json", "r") as f:
    opts = json.load(f)

TOKENS = opts.get("tokens", [])
IP_WHITELIST = opts.get("whitelist", [])
DEFAULT_DAY = opts.get("default_day")
DEFAULT_HOUR = opts.get("default_hour")
EMAIL = opts.get("email")
PASSWORD = opts.get("password")
SPORT = opts.get("sport")
LOCATION = opts.get("location")


@app.route("/")
def home():
    return "Selenium Reservation Server is running!"

@app.route("/run", methods=["GET","POST"])
def run_selenium():
    # Whitelist check
    client_ip = request.remote_addr
    if IP_WHITELIST and client_ip not in IP_WHITELIST:
        return f"Forbidden: IP {client_ip} not allowed", 403

    # Token check
    if TOKENS:
        token = request.headers.get("X-Token")
        if not token:
            return "Unauthorized: Missing X-Token header", 401 # No header
        if token not in TOKENS:
            return "Unauthorized: Invalid token", 401    

    # Get params & build env
    day = DEFAULT_DAY
    hour = DEFAULT_HOUR
    email = EMAIL
    password = PASSWORD
    sport = SPORT
    location = LOCATION
    
    env = os.environ.copy()
    env["TARGET_DAY_NAME"] = day
    env["TARGET_HOUR"] = hour
    env["EMAIL"] = email
    env["PASSWORD"] = password
    env["SPORT"] = sport
    env["LOCATION"] = location

    subprocess.Popen(["python3", "/selenium_script.py"], env=env)
    return f"Selenium script started! DAY={day}, HOUR={hour}"

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
