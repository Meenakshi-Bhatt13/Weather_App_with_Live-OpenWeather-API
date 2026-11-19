
import requests
import os
import time

from dotenv import load_dotenv
from datetime import datetime


# ==========================================
# PROJECT 05: WEATHER APP
# ==========================================

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5"

CACHE_DURATION = 600  # 10 minutes

# Store recently fetched weather data
weather_cache = {}


# ==========================================
# 1. FETCH DATA FROM WEATHER API
# ==========================================

def get_weather_data(endpoint, city):

    url = f"{BASE_URL}/{endpoint}"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError:

        if response.status_code == 404:
            print("Error: City not found.")

        elif response.status_code == 401:
            print("Error: Invalid API key or key not activated.")

        elif response.status_code == 429:
            print("Error: API request limit reached.")

        else:
            print("HTTP Error:", response.status_code)

    except requests.exceptions.Timeout:
        print("Error: Request timed out. Try again.")

    except requests.exceptions.ConnectionError:
        print("Error: Please check your internet connection.")

    except requests.exceptions.RequestException as error:
        print("Request failed:", error)

    except ValueError:
        print("Error: Unable to read the API response.")

    return None


# ==========================================
# 2. GET CURRENT WEATHER AND FORECAST
# ==========================================

def fetch_weather(city):

    cache_key = city.strip().lower()

    # Check cached data
    if cache_key in weather_cache:

        cached_data = weather_cache[cache_key]

        if time.time() - cached_data["time"] < CACHE_DURATION:

            print("\nShowing recently cached weather data.")

            return cached_data["current"], cached_data["forecast"]

    print("\nFetching live weather information...")

    # Get current weather
    current = get_weather_data("weather", city)

    if current is None:
        return None, None

    # Get five-day forecast
    forecast = get_weather_data("forecast", city)

    # Save data in cache
    weather_cache[cache_key] = {
        "time": time.time(),
        "current": current,
        "forecast": forecast
    }

    return current, forecast


# ==========================================
# 3. DISPLAY CURRENT WEATHER
# ==========================================

def display_current_weather(data):

    if not data:
        return

    print("\n" + "=" * 45)
    print("             CURRENT WEATHER")
    print("=" * 45)

    city = data.get("name", "Unknown")
    country = data.get("sys", {}).get("country", "")

    main_data = data.get("main", {})
    weather_list = data.get("weather", [])

    temperature = main_data.get("temp", "N/A")
    feels_like = main_data.get("feels_like", "N/A")
    humidity = main_data.get("humidity", "N/A")

    description = "N/A"

    if weather_list:
        description = weather_list[0].get(
            "description", "N/A"
        )

    wind_speed = data.get("wind", {}).get("speed", "N/A")

    print(f"City          : {city}, {country}")
    print(f"Temperature   : {temperature} °C")
    print(f"Feels Like    : {feels_like} °C")
    print(f"Humidity      : {humidity}%")
    print(f"Weather       : {description.title()}")
    print(f"Wind Speed    : {wind_speed} m/s")

    print("=" * 45)


# ==========================================
# 4. DISPLAY FIVE-DAY FORECAST
# ==========================================

def display_forecast(data):

    print("\n" + "=" * 65)
    print("                  FIVE-DAY FORECAST")
    print("=" * 65)

    if not data or not data.get("list"):
        print("Forecast information is unavailable.")
        return

    # Group forecast entries by date
    daily_data = {}

    for item in data["list"]:

        date_time = datetime.strptime(
            item["dt_txt"],
            "%Y-%m-%d %H:%M:%S"
        )

        date = date_time.strftime("%Y-%m-%d")

        # Select the forecast closest to 12 PM
        if date not in daily_data:

            daily_data[date] = item

        else:

            existing_time = datetime.strptime(
                daily_data[date]["dt_txt"],
                "%Y-%m-%d %H:%M:%S"
            )

            if abs(date_time.hour - 12) < abs(existing_time.hour - 12):
                daily_data[date] = item

    print(f"{'Date':<15}{'Temp (C)':<15}{'Weather'}")
    print("-" * 65)

    # Display up to five forecast days
    for date, item in list(daily_data.items())[:5]:

        temperature = item.get("main", {}).get("temp", "N/A")

        weather_list = item.get("weather", [])

        description = "N/A"

        if weather_list:
            description = weather_list[0].get(
                "description", "N/A"
            )

        print(
            f"{date:<15}"
            f"{str(temperature):<15}"
            f"{description.title()}"
        )

    print("=" * 65)


# ==========================================
# 5. MAIN WEATHER APPLICATION
# ==========================================

def main():

    print("\n======================================")
    print("       WEATHER APP WITH OPENWEATHER")
    print("======================================")

    # Check API key
    if not API_KEY:

        print("\nAPI key not found!")
        print("Please add OPENWEATHER_API_KEY to your .env file.")
        return

    while True:

        print("\nEnter a city name to check its weather.")
        print("Press ENTER without typing a city to exit.")

        city = input("\nEnter city name: ").strip()

        # Exit application
        if not city:
            print("\nThank you for using Weather App!")
            break

        # Fetch weather information
        current, forecast = fetch_weather(city)

        if current is None:
            continue

        # Display current weather
        display_current_weather(current)

        # Display forecast
        display_forecast(forecast)


# ==========================================
# PROGRAM EXECUTION
# ==========================================

if __name__ == "__main__":
    main()
