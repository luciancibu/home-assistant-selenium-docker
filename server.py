from flask import Flask, request
import subprocess
import os

app = Flask(__name__)

SECRET_TOKEN = "your-token

@app.route("/")
def home():
    return "Selenium Reservation Server is running!"

@app.route("/run", methods=["GET","POST"])
def run_selenium():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return "Unauthorized: Missing or invalid Authorization header", 401
    token = auth_header.split(" ")[1] # Get token
    if token != SECRET_TOKEN:
        return "Unauthorized: Invalid token", 401    

    day = request.args.get("day")
    hour = request.args.get("hour")
    env = os.environ.copy()
    env["TARGET_DAY_NAME"] = day
    env["TARGET_HOUR"] = hour

    subprocess.Popen(["python3", "/selenium_script.py"], env=env)
    return f"Selenium script started! DAY={day}, HOUR={hour}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
