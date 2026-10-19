
import os

import requests
from dotenv import load_dotenv

# Read the token from the local .env file
load_dotenv()

token = os.getenv("WAQI_API_TOKEN")

if not token or token == "paste_your_token_here":
    print("ERROR: WAQI_API_TOKEN was not found in .env.")
    raise SystemExit(1)

print("Token found. Testing WAQI API connection...")

url = "https://api.waqi.info/feed/hyderabad/"

try:
    response = requests.get(
        url,
        params={"token": token},
        timeout=20,
    )
    response.raise_for_status()
    result = response.json()

    if result.get("status") == "ok":
        data = result.get("data", {})
        print("SUCCESS: WAQI API connection works!")
        print("Station:", data.get("city", {}).get("name", "Unknown"))
        print("AQI:", data.get("aqi", "Unavailable"))
        print("Token was not displayed.")
    else:
        print("WAQI returned status:", result.get("status"))
        print("Message:", result.get("data", "No details provided"))

except requests.RequestException as error:
    print("Connection error:", type(error).__name__)
    print("Check your internet connection and try again.")
