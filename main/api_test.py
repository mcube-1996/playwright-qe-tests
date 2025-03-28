import requests
import logging
import config  # Import the API key from config.py

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class WeatherAPITest:
    def __init__(self):
        self.api_key = config.API_KEY  # Use API key from config.py
        self.base_url = "https://api.weatherbit.io/v2.0/current"

    def get_weather_by_city(self, city, country):
        """Fetch current weather data using city name and country code."""
        params = {
            "city": city,
            "country": country,
            "key": self.api_key
        }
        response = requests.get(self.base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]:
                weather = data["data"][0]
                logging.info(f"Weather in {city}: {weather['temp']}°C, {weather['weather']['description']}")
            else:
                logging.warning(f"No weather data found for {city}.")
        else:
            logging.error(f"Failed to fetch weather for {city}. Status: {response.status_code}")


if __name__ == "__main__":
    weather_test = WeatherAPITest()

    # Fetch weather for Sydney, Australia
    weather_test.get_weather_by_city("Sydney", "AU")

    # Fetch weather for New York, USA
    weather_test.get_weather_by_city("New York", "US")
