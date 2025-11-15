from flask import Flask
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return "Selenium Reservation Server is running!"

@app.route("/run", methods=["GET","POST"])
def run_selenium():
    subprocess.Popen(["python3", "/selenium_script.py"])
    return "Selenium script started!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)