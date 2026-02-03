import os
import requests
from flask import Flask, render_template, request, jsonify
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

@app.route("/api/suggestions")
def get_suggestions():
    query = request.args.get('q')
    if not query:
        return jsonify([])
    
    api_key = os.getenv("API_KEY")
    if not api_key:
        return jsonify({"error": "API key missing"}), 500

    url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        suggestions = []
        for item in data:
            location = f"{item['name']}"
            if 'state' in item:
                location += f", {item['state']}"
            if 'country' in item:
                location += f", {item['country']}"
            suggestions.append(location)
            
        return jsonify(suggestions)
    except Exception as e:
        print(f"Error fetching suggestions: {e}")
        return jsonify([])

@app.route("/api/images")
def get_images():
    query = request.args.get('query')
    if not query:
        return jsonify([])

    unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not unsplash_key:
        print("Unsplash API key missing")
        return jsonify([])

    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": 5,
        "orientation": "landscape" # Better for sliders usually, checking reqs.. vertical or horizontal slider requested. 
    }
    # User asked for rotating images on right side.. maybe portrait or landscape?
    # Req: "Add a vertical or horizontal image slider on the RIGHT side"
    # Regular urls working best.

    headers = {
        "Authorization": f"Client-ID {unsplash_key}"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        images = []
        for item in data.get('results', []):
            images.append({
                "url": item['urls']['regular'],
                "alt": item.get('alt_description', 'Location image'),
                "credit": item['user']['name'],
                "credit_url": item['user']['links']['html']
            })
            
        return jsonify(images)
    except Exception as e:
        print(f"Error fetching images: {e}")
        return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)
