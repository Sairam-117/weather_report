import os
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

app = Flask(__name__)

def get_weather(city_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetches weather data for a specific city from OpenWeatherMap.
    Same logic as our CLI tool!
    """
    api_key = os.getenv("API_KEY")
    if not api_key:
        return None

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    url = f"{base_url}?appid={api_key}&q={city_name}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    error_message = None

    if request.method == "POST":
        city = request.form.get("city")
        if city:
            data = get_weather(city)
            if data:
                weather_data = {
                    "city": data["name"],
                    "description": data["weather"][0]["description"].capitalize(),
                    "temp": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "icon": data["weather"][0]["icon"]
                }
            else:
                error_message = f"City '{city}' not found or API error."
        else:
            error_message = "Please enter a city name."

    return render_template("index.html", weather=weather_data, error=error_message)

if __name__ == "__main__":
    app.run(debug=True)
