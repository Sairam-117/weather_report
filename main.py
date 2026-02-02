import os
import requests
import sys
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_weather(city_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetches weather data for a specific city from OpenWeatherMap.

    Args:
        city_name (str): The name of the city to query.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing weather data if successful, None otherwise.
    """
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("Error: API_KEY not found in .env file.")
        return None

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    url = f"{base_url}?appid={api_key}&q={city_name}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an error for 4xx/5xx status codes
        return response.json()
    except requests.exceptions.HTTPError as err:
        if response.status_code == 404:
            print(f"Error: City '{city_name}' not found.")
        elif response.status_code == 401:
            print("Error: Unauthorized. Please check your API key.")
        else:
            print(f"HTTP Error: {err}")
    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
    
    return None

def display_weather(data: Dict[str, Any]) -> None:
    """
    Parses and prints the weather data in a readable format.

    Args:
        data (Dict[str, Any]): The weather data dictionary returned by the API.
    """
    if not data:
        return

    city = data.get('name')
    weather_desc = data['weather'][0]['description'].capitalize()
    temp = data['main']['temp']
    humidity = data['main']['humidity']

    print("\n-------------------------")
    print(f"Weather in {city}:")
    print(f"Condition:   {weather_desc}")
    print(f"Temperature: {temp}°C")
    print(f"Humidity:    {humidity}%")
    print("-------------------------\n")

def main() -> None:
    """
    Main application loop.
    """
    print("Welcome to the Python Weather App!")
    print("Type 'exit' or 'quit' to stop the application.\n")

    while True:
        try:
            city = input("Enter city name: ").strip()

            if city.lower() in ('exit', 'quit'):
                print("Goodbye!")
                break
            
            if not city:
                print("Please enter a valid city name.")
                continue

            weather_data = get_weather(city)
            if weather_data:
                display_weather(weather_data)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
