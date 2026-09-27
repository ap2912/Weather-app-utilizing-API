# Weather / Now

A premium, minimal weather website. Enter any city and instantly see its
current weather — no page refresh, no API key, no clutter.

Built with **Python + Flask** on the backend and **vanilla JavaScript**
on the frontend, styled in a dark editorial **black + Spider-Man red**
identity over a cinematic local background video.

## Features

- Search any city, press Enter or click CHECK →
- Current temperature (oversized), weather condition, humidity,
  feels-like temperature, wind speed
- Day/night indicator and timezone
- Graceful error states: unknown city, empty input, service outages
- Subtle fade/slide-in animations, lime focus states, loading indicator
- Fully responsive: desktop, laptop, tablet, mobile
- Accessible: semantic HTML, keyboard navigation, visible focus states,
  `aria-live` regions for results and errors

## Technologies

- Python 3, Flask — backend and routing
- `requests` — all weather API communication
- HTML, CSS, vanilla JavaScript — frontend (no frameworks)
- gunicorn — production server

## API used

[Open-Meteo](https://open-meteo.com) — free, no API key required.

### How the API flow works

```text
USER
 ↓
WEBSITE
 ↓
FLASK
 ↓
OPEN-METEO GEOCODING
 ↓
LATITUDE + LONGITUDE
 ↓
OPEN-METEO WEATHER API
 ↓
JSON
 ↓
FLASK
 ↓
WEBSITE
```

1. The frontend sends the city to `GET /api/weather?city=Riga`.
2. Flask validates the city and calls the **Geocoding API**
   (`https://geocoding-api.open-meteo.com/v1/search`) with query params
   via `requests` — user input is never concatenated into a URL.
3. The best match yields latitude, longitude, and timezone.
4. Flask calls the **Forecast API**
   (`https://api.open-meteo.com/v1/forecast`) requesting current
   `temperature_2m`, `relative_humidity_2m`, `apparent_temperature`,
   `weather_code`, `wind_speed_10m`, and `is_day`.
5. The JSON response is parsed, WMO weather codes are converted to
   readable conditions, and the data is normalized into a clean contract:

```json
{
  "city": "Riga",
  "country": "Latvia",
  "timezone": "Europe/Riga",
  "temperature": 14,
  "feels_like": 13,
  "humidity": 72,
  "wind_speed": 12,
  "condition": "Partly cloudy",
  "is_day": true
}
```

6. Flask returns this JSON; the frontend renders it without reloading.

Raw upstream responses are never exposed to the browser.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## How to run it

Development:

```bash
python app.py
```

Then open http://127.0.0.1:5000/

Production:

```bash
gunicorn app:app
```

## Example usage

```text
Search field:  Riga          [CHECK →]

RIGA, LATVIA ●

15°
MAINLY CLEAR

HUMIDITY        69%
FEELS LIKE      14°
WIND            7 KM/H

EUROPE/RIGA
```

## Error handling

The site never shows a traceback or a broken layout:

| Problem | Backend | Frontend shows |
|---|---|---|
| Empty input | `400 {"error": "empty_city"}` | CITY NOT FOUND — please type a city name |
| Unknown city | `404 {"error": "city_not_found"}` | CITY NOT FOUND — We couldn't find that location. Try searching for another city. |
| Network / HTTP / timeout / bad JSON / missing fields | `502 {"error": "service_unavailable"}` | WEATHER SERVICE UNAVAILABLE — Please try again. |

Every upstream call uses a 10-second timeout and `response.raise_for_status()`;
failures are caught via `requests.exceptions.RequestException`. Unknown
weather codes fall back to `"Unknown conditions"`. The frontend also
prevents duplicate requests while one is in flight.

## Theme & background video

The visual theme is **black + Spider-Man red** (`--accent: #E10600`,
`--accent-bright: #FF1A1A`): red temperature, red CHECK button, red
focus states, red location dot, red stat values — with the weather
cards themselves staying dark.

The page background is a local video file:

```text
static/video/spiderman.mp4
```

Place your own `spiderman.mp4` in `static/video/` — the site loads it
from `/static/video/spiderman.mp4` via a native HTML5 `<video>` element
(`autoplay`, `muted`, `loop`, `playsinline`, `aria-hidden="true"`).
A dark gradient overlay (~70–85% darkening) keeps the UI readable while
the video stays clearly visible. If the file is missing, the site falls
back to the plain black/red background with no errors.

## Project structure

```text
weather-app/
├── app.py               # Flask routes + Open-Meteo logic via requests
├── requirements.txt     # Flask, requests, gunicorn
├── README.md            # this file
├── SKILLS.md            # project brief / spec
├── .gitignore
├── templates/
│   └── index.html       # semantic markup, aria-live regions
└── static/
    ├── style.css        # black/red editorial design, responsive
    ├── script.js        # fetch, loading, errors, DOM updates (vanilla JS)
    └── video/
        └── spiderman.mp4  # your local background video (you provide it)
```

## What was learned

- Taking user input from a web form and validating it server-side
- Making HTTP requests with `requests`, using `params` for query strings
- Setting timeouts and using `raise_for_status()` for robust API calls
- Catching `requests.exceptions.RequestException` for network failures
- Parsing JSON and extracting nested values from dictionaries
- Normalizing raw API data into a clean data contract for the frontend
- Mapping numeric codes to readable labels with a fallback
- Building Flask routes that serve both pages and JSON APIs
- Updating the DOM with vanilla JavaScript: fetch, loading states,
  error states, and duplicate-request prevention
- Designing a responsive, accessible dark UI
