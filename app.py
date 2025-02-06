import requests
from flask import Flask, request, json
from urllib.parse import urlparse, parse_qs
import re
from datetime import datetime, timedelta
import os
import pytz

TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
GRAFANA_URL = os.getenv('GRAFANA_URL')

WIB = pytz.timezone('Asia/Jakarta')

if not TOKEN or not CHAT_ID or not GRAFANA_URL:
    raise ValueError("Error: Missing environment variables. Exiting...")

app = Flask(__name__)

def generate_renderer_url(panel_url):
    """Generate a Grafana renderer URL from the panel URL."""
    # Parse the panel URL to extract dashboard UID and panel ID
    match = re.search(r'/d/([^/?]+)', panel_url)
    dashboard_uid = match.group(1) if match else None

    query_params = parse_qs(urlparse(panel_url).query)
    panel_id = query_params.get("viewPanel", [None])[0]  # Default ke None jika tidak ada viewPanel

    if not dashboard_uid or not panel_id:
        raise ValueError("Invalid panel URL: Could not extract dashboard UID or panel ID")

    # Calculate time range (e.g., last 5 minutes)
    now = datetime.now()
    five_minutes_ago = now - timedelta(minutes=5)
    from_time = five_minutes_ago.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    to_time = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    # Construct the renderer URL
    renderer_url = (
        f"{GRAFANA_URL}/render/d-solo/{dashboard_uid}?"
        f"panelId={panel_id}&width=1000&height=500&"
        f"from={from_time}&to={to_time}&tz=Asia%2FJakarta"
    )
    print(renderer_url)
    return renderer_url

def send_telegram_photo(image_url, message, alert_id):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    data = {"chat_id": CHAT_ID, "caption": message}
    files = {"photo": requests.get(image_url).content}

    response = requests.post(url, data=data, files=files)
    print(response.json())  # Debugging


@app.route('/grafana-webhook', methods=['POST'])
def grafana_alert():
    """Receive Grafana alert and send it to Telegram"""
    alert_data = request.json
    if not alert_data:
        return "No data received", 400

    print(alert_data)

    # Extract data from Grafana payload
    alert_title = alert_data.get("title", "No Title")
    alert_message = alert_data.get("message", "No message provided")
    image_url = alert_data.get("imageURL")  # Grafana alert image
    panel_url = alert_data.get("alerts", [{}])[0].get("panelURL") # Grafana alert image

    print(panel_url)

    # Construct Telegram message
    message = f"{alert_message}"

    if panel_url:
        send_telegram_photo(generate_renderer_url(panel_url), message, alert_title)  # Send alert with image
    else:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        )

    return "OK", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

