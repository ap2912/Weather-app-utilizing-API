"""
app.py — Weather / Now.

Flask backend for the weather website. Receives a city name from the
frontend, uses the `requests` library to talk to the free Open-Meteo
API (geocoding -> forecast), normalizes the JSON into a clean data
contract, and returns it to the frontend.

No raw API responses are exposed. No API key is needed.
"""

import logging
import time

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

REQUEST_TIMEOUT = 15  # seconds per attempt
MAX_ATTEMPTS = 3      # total tries before giving up
RETRY_DELAY = 2       # seconds to wait between attempts

# A descriptive User-Agent: some networks/WAFs treat the default
# python-requests UA worse than an identified client.
HEADERS = {"User-Agent": "WeatherNow/1.0 (educational project)"}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather-now")

# WMO weather interpretation codes, as documented by Open-Meteo.
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Fog",
    51: "Drizzle",
    53: "Drizzle",
    55: "Drizzle",
    56: "Freezing drizzle",
    57: "Freezing drizzle",
    61: "Rain",
    63: "Rain",
    65: "Rain",
    66: "Freezing rain",
    67: "Freezing rain",
    71: "Snow",
    73: "Snow",
    75: "Snow",
    77: "Snow grains",
    80: "Rain showers",
    81: "Rain showers",
    82: "Rain showers",
    85: "Snow showers",
    86: "Snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with hail",
}


class CityNotFoundError(Exception):
    """Raised when the geocoding API finds no matching city."""


class WeatherAPIError(Exception):
    """Raised on network, HTTP, JSON, or malformed-data failures."""


def get_weather_condition(code):
    """Convert a WMO weather code into a human-readable condition."""
    return WEATHER_CODES.get(code, "Unknown conditions")


def fetch_json(url, params):
    """GET `url` with query params, return parsed JSON.

    Always sends params via `requests` (never hand-built URLs),
    enforces a timeout, retries transient failures, logs the real
    reason server-side, and raises WeatherAPIError if all attempts fail.
    """
    last_exc = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(
                url, params=params, timeout=REQUEST_TIMEOUT, headers=HEADERS
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            last_exc = exc
            status = (
                exc.response.status_code
                if getattr(exc, "response", None) is not None
                else "no-response"
            )
            logger.warning(
                "Upstream request failed (attempt %d/%d, status=%s): %s -- %s",
                attempt, MAX_ATTEMPTS, status, url, exc,
            )
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY)
            continue

        try:
            return response.json()
        except ValueError as exc:
            raise WeatherAPIError("Upstream service returned invalid JSON.") from exc

    raise WeatherAPIError(
        f"Upstream request failed after {MAX_ATTEMPTS} attempts: {last_exc}"
    ) from last_exc


def geocode_city(city):
    """Resolve a city name to coordinates via the Open-Meteo Geocoding API."""
    payload = fetch_json(
        GEOCODING_URL,
        {"name": city, "count": 1, "language": "en", "format": "json"},
    )

    results = payload.get("results")
    if not results:
        raise CityNotFoundError(f"No location found for '{city}'.")

    place = results[0]
    return {
        "city": place.get("name", city),
        "country": place.get("country", "Unknown"),
        "latitude": place.get("latitude"),
        "longitude": place.get("longitude"),
        "timezone": place.get("timezone", "Unknown"),
    }


def fetch_weather(latitude, longitude):
    """Fetch current weather for coordinates and normalize the data."""
    payload = fetch_json(
        FORECAST_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "weather_code,"
                "wind_speed_10m,"
                "is_day"
            ),
            "timezone": "auto",
        },
    )

    current = payload.get("current")
    if not isinstance(current, dict):
        raise WeatherAPIError("Weather service returned unexpected data.")

    try:
        return {
            "temperature": round(current["temperature_2m"]),
            "feels_like": round(current["apparent_temperature"]),
            "humidity": current["relative_humidity_2m"],
            "wind_speed": round(current["wind_speed_10m"]),
            "condition": get_weather_condition(current["weather_code"]),
            "is_day": bool(current["is_day"]),
        }
    except KeyError as exc:
        raise WeatherAPIError(f"Weather data is missing a field: {exc}") from exc


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/weather")
def api_weather():
    city = (request.args.get("city") or "").strip()

    if not city:
        return jsonify({"error": "empty_city"}), 400

    try:
        location = geocode_city(city)
        weather = fetch_weather(location["latitude"], location["longitude"])
    except CityNotFoundError:
        return jsonify({"error": "city_not_found"}), 404
    except WeatherAPIError:
        # Never leak tracebacks or upstream details to the browser.
        return jsonify({"error": "service_unavailable"}), 502

    return jsonify(
        {
            "city": location["city"],
            "country": location["country"],
            "timezone": location["timezone"],
            "temperature": weather["temperature"],
            "feels_like": weather["feels_like"],
            "humidity": weather["humidity"],
            "wind_speed": weather["wind_speed"],
            "condition": weather["condition"],
            "is_day": weather["is_day"],
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
