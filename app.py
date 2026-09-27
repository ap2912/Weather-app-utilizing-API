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

# Fallback forecast provider: the Norwegian Meteorological Institute.
# Free, no API key needed, but it requires an identifying User-Agent.
METNO_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
METNO_HEADERS = {"User-Agent": "WeatherNow/1.0 (educational project)"}

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


def fetch_json(url, params, headers=None):
    """GET `url` with query params, return parsed JSON.

    Always sends params via `requests` (never hand-built URLs),
    enforces a timeout, retries transient failures, logs the real
    reason server-side, and raises WeatherAPIError if all attempts fail.

    A 429 (rate limit) is never retried: hammering a capped endpoint
    cannot succeed, so we fail fast and let the caller fall back.
    """
    last_exc = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT,
                headers=headers or HEADERS,
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
            if status == 429 or attempt >= MAX_ATTEMPTS:
                break
            time.sleep(RETRY_DELAY)
            continue

        try:
            return response.json()
        except ValueError as exc:
            raise WeatherAPIError("Upstream service returned invalid JSON.") from exc

    raise WeatherAPIError(
        f"Upstream request failed after {attempt} attempt(s): {last_exc}"
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


def fetch_open_meteo(latitude, longitude):
    """Primary forecast via Open-Meteo. Returns the normalized weather dict."""
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


def apparent_temperature(temp_c, humidity, wind_kmh):
    """Rough 'feels like': wind chill when cold, heat index when hot."""
    if temp_c <= 10 and wind_kmh > 4.8:
        v = wind_kmh ** 0.16  # wind chill formula (Environment Canada)
        return 13.12 + 0.6215 * temp_c - 11.37 * v + 0.3965 * temp_c * v
    if temp_c >= 27:  # Rothfusz heat-index regression
        t_f = temp_c * 9 / 5 + 32
        hi_f = (
            -42.379
            + 2.04901523 * t_f
            + 10.14333127 * humidity
            - 0.22475541 * t_f * humidity
            - 0.00683783 * t_f * t_f
            - 0.05481717 * humidity * humidity
            + 0.00122874 * t_f * t_f * humidity
            + 0.00085282 * t_f * humidity * humidity
            - 0.00000199 * t_f * t_f * humidity * humidity
        )
        return (hi_f - 32) * 5 / 9
    return temp_c


def metno_condition(symbol_code):
    """Convert a met.no symbol_code (e.g. 'partlycloudy_day') to readable text."""
    if not symbol_code:
        return "Unknown"
    base = symbol_code.replace("_day", "").replace("_night", "")
    names = {
        "clearsky": "Clear sky",
        "fair": "Fair",
        "partlycloudy": "Partly cloudy",
        "cloudy": "Cloudy",
        "lightrainshowers": "Light rain showers",
        "rainshowers": "Rain showers",
        "heavyrainshowers": "Heavy rain showers",
        "lightrain": "Light rain",
        "rain": "Rain",
        "heavyrain": "Heavy rain",
        "lightsnowshowers": "Light snow showers",
        "snowshowers": "Snow showers",
        "heavysnowshowers": "Heavy snow showers",
        "lightsnow": "Light snow",
        "snow": "Snow",
        "heavysnow": "Heavy snow",
        "lightsleetshowers": "Light sleet showers",
        "sleetshowers": "Sleet showers",
        "heavysleetshowers": "Heavy sleet showers",
        "lightsleet": "Light sleet",
        "sleet": "Sleet",
        "heavysleet": "Heavy sleet",
        "fog": "Fog",
    }
    if base in names:
        return names[base]
    if "thunder" in base:
        return "Thunderstorm"
    return base.replace("_", " ").strip().title() or "Unknown"


def fetch_metno(latitude, longitude):
    """Fallback forecast via met.no (no API key). Returns normalized weather dict."""
    payload = fetch_json(
        METNO_URL,
        {"lat": latitude, "lon": longitude},
        headers=METNO_HEADERS,
    )

    try:
        now = payload["properties"]["timeseries"][0]
        details = now["data"]["instant"]["details"]
        symbol = None
        for key in ("next_1_hours", "next_6_hours"):
            block = now["data"].get(key) or {}
            symbol = (block.get("summary") or {}).get("symbol_code")
            if symbol:
                break
    except (KeyError, IndexError, TypeError) as exc:
        raise WeatherAPIError("Fallback service returned unexpected data.") from exc

    temperature = details.get("air_temperature")
    if temperature is None:
        raise WeatherAPIError("Fallback service returned unexpected data.")
    humidity = details.get("relative_humidity") or 0
    wind_ms = details.get("wind_speed") or 0
    wind_kmh = wind_ms * 3.6  # met.no uses m/s; our contract uses km/h

    return {
        "temperature": round(temperature),
        "feels_like": round(apparent_temperature(temperature, humidity, wind_kmh)),
        "humidity": round(humidity),
        "wind_speed": round(wind_kmh),
        "condition": metno_condition(symbol),
        "is_day": not (symbol or "").endswith("_night"),
    }


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
    except CityNotFoundError:
        return jsonify({"error": "city_not_found"}), 404
    except WeatherAPIError:
        # Never leak tracebacks or upstream details to the browser.
        return jsonify({"error": "service_unavailable"}), 502

    # Primary provider first; if it is rate-limited or down, degrade
    # gracefully to the fallback instead of failing the request.
    try:
        weather = fetch_open_meteo(location["latitude"], location["longitude"])
        source = "open-meteo"
    except WeatherAPIError as exc:
        logger.warning("Primary forecast failed (%s); trying met.no fallback.", exc)
        try:
            weather = fetch_metno(location["latitude"], location["longitude"])
            source = "met.no"
        except WeatherAPIError:
            return jsonify({"error": "service_unavailable"}), 502

    return jsonify(
        {
            "city": location["city"],
            "country": location["country"],
            "timezone": location["timezone"],
            "source": source,
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
