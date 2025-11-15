from flask import Flask, request
import subprocess
import os

app = Flask(__name__)

with open("/data/options.json", "r") as f:
    opts = json.load(f)

TOKENS = opts.get("tokens", [])
IP_WHITELIST = opts.get("whitelist", [])

@app.route("/")
def home():
    return "Selenium Reservation Server is running!"

@app.route("/run", methods=["GET","POST"])
def run_selenium():
    # Whitelist check
    client_ip = request.remote_addr
    if client_ip not in IP_WHITELIST:
        return f"Forbidden: IP {client_ip} not allowed", 403

    # Token check
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return "Unauthorized: Missing or invalid Authorization header", 401
    token = auth_header.split(" ")[1] # Get token
    if token not in TOKENS:
        return "Unauthorized: Invalid token", 401    

    # Get params
    day = request.args.get("day")
    hour = request.args.get("hour")
    env = os.environ.copy()
    env["TARGET_DAY_NAME"] = day
    env["TARGET_HOUR"] = hour

    # Run script
    subprocess.Popen(["python3", "/selenium_script.py"], env=env)
    return f"Selenium script started! DAY={day}, HOUR={hour}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
