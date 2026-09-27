# SKILLS.md — Weather / Now

## Project Goal

Create a **premium weather website** where a user can enter any city and instantly see its current weather.

The project must use **Python + Flask** as the backend and the `requests` library to communicate with a free weather API.

The final result should look and feel like a real polished web product, not a basic Python school exercise.

---

# Core Requirements

The website must:

1. Allow the user to enter a city name.
2. Send that city to the Python backend.
3. Use Python's `requests` library to call a free weather API.
4. Receive weather data as JSON.
5. Extract the required values from the JSON response.
6. Display:
   - City
   - Country
   - Temperature
   - Weather condition
   - Humidity
   - Feels-like temperature
   - Wind speed
7. Handle invalid cities gracefully.
8. Handle API/network errors gracefully.
9. Have a polished responsive UI.
10. Be ready to deploy to GitHub/GitHub Pages-compatible hosting or a Python-capable host.

---

# Technology Stack

## Backend

Use:

- Python
- Flask
- requests

## Frontend

Use:

- HTML5
- CSS3
- Vanilla JavaScript

Do NOT use React, Vue, Tailwind, Bootstrap, or other frameworks unless explicitly requested.

The project should remain simple enough for a beginner to understand.

---

# Weather API

Use **Open-Meteo**.

Open-Meteo does not require an API key for normal non-commercial use.

### Geocoding endpoint

```text
https://geocoding-api.open-meteo.com/v1/search
```

Use it to convert the user's city name into:

- city
- country
- latitude
- longitude
- timezone

### Weather endpoint

```text
https://api.open-meteo.com/v1/forecast
```

Use it to retrieve current weather.

Recommended current fields:

```text
temperature_2m
relative_humidity_2m
apparent_temperature
weather_code
wind_speed_10m
is_day
```

Useful documentation:

```text
https://open-meteo.com/en/docs/geocoding-api
https://open-meteo.com/en/docs
```

---

# Project Structure

Use this structure:

```text
weather-app/
│
├── app.py
├── requirements.txt
├── README.md
├── SKILLS.md
├── .gitignore
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js
```

---

# Backend — Flask

`app.py` should:

1. Create the Flask application.
2. Serve the main page.
3. Receive city searches.
4. Call the Open-Meteo geocoding API.
5. Select a matching location.
6. Call the weather API using latitude and longitude.
7. Parse the JSON.
8. Convert the weather code into readable text.
9. Return clean JSON to the frontend.

Prefer an API route such as:

```text
GET /api/weather?city=Riga
```

Example frontend request:

```javascript
fetch(`/api/weather?city=${encodeURIComponent(city)}`)
```

---

# API Request Requirements

Use `requests` with query parameters.

Example:

```python
response = requests.get(
    url,
    params=params,
    timeout=10
)

response.raise_for_status()
data = response.json()
```

Do NOT manually concatenate user input into URLs.

Use:

```python
params={}
```

instead.

---

# Suggested Backend Functions

Keep the Python code modular.

Recommended functions:

```python
def get_location(city):
    ...

def get_weather(latitude, longitude):
    ...

def weather_code_to_text(code):
    ...

def build_weather_response(location, weather):
    ...
```

The exact implementation can vary.

Avoid putting the entire application inside one giant function.

---

# Weather Code Mapping

Convert WMO weather codes into readable conditions.

At minimum:

```text
0       Clear sky
1       Mainly clear
2       Partly cloudy
3       Overcast

45, 48  Fog

51,53,55 Drizzle
56,57   Freezing drizzle

61,63,65 Rain
66,67   Freezing rain

71,73,75 Snow
77      Snow grains

80,81,82 Rain showers
85,86   Snow showers

95      Thunderstorm
96,99   Thunderstorm with hail
```

Unknown codes should fall back to:

```text
Unknown conditions
```

---

# JSON Response

Normalize the API data before sending it to the frontend.

Return a structure similar to:

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

The frontend should NOT need to understand the raw Open-Meteo JSON structure.

---

# Error Handling

The backend must gracefully handle:

### Empty city

Return an appropriate HTTP error such as:

```text
Please enter a city.
```

### City not found

Display:

```text
City not found.
Try another city.
```

### Network/API error

Display:

```text
Weather service unavailable.
Please try again.
```

### Unexpected response

Do not expose Python tracebacks to the user.

Use clean error messages.

Use:

```python
requests.exceptions.RequestException
```

for request-related errors.

Set a timeout:

```python
timeout=10
```

---

# Frontend Design

## Overall Aesthetic

The website must reuse the visual identity from the user's previous password-generator project.

### Design direction

**Premium**
**Minimal**
**Dark**
**Editorial**
**Technical**
**Futuristic**
**Apple-inspired**

The site should feel like an expensive weather utility.

It should NOT look like:

- a generic weather template
- a school project
- a Bootstrap dashboard
- a cartoon weather app
- an over-designed glassmorphism template
- an AI-generated UI with random gradients

---

# Color Palette

Primary background:

```text
#050505
```

Secondary surfaces:

```text
#0B0B0B
#111111
```

Primary text:

```text
#F5F5F5
```

Secondary text:

```text
#8A8A8A
```

Accent:

```text
Lime / Electric Green
```

The lime accent should be used carefully.

Use it for:

- buttons
- focus states
- active indicators
- small decorative lines
- important values
- subtle glow
- status indicators

Black should remain the dominant color.

---

# Typography

Use a modern geometric/editorial sans-serif.

The typography should resemble the previous website's style.

Prioritize:

- large numbers
- uppercase micro-labels
- generous letter spacing
- strong visual hierarchy
- clean spacing

Example:

```text
WEATHER / NOW

RIGA, LATVIA

14°

PARTLY CLOUDY
```

The temperature should be one of the largest elements on the page.

---

# Page Layout

Desktop layout should roughly follow:

```text
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  WEATHER / NOW                                  09.27.26   │
│                                                            │
│  ────────────────────────────────────────────────────────  │
│                                                            │
│  CURRENT WEATHER                                           │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                                                      │  │
│  │  SEARCH ANY CITY...                         →        │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  RIGA, LATVIA                                              │
│                                                            │
│  14°                         PARTLY CLOUDY                  │
│                                                            │
│  CURRENT                                                   │
│                                                            │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ │
│  │ HUMIDITY       │ │ FEELS LIKE     │ │ WIND           │ │
│  │ 72%            │ │ 13°            │ │ 12 KM/H        │ │
│  └────────────────┘ └────────────────┘ └────────────────┘ │
│                                                            │
│  EUROPE/RIGA                                               │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

This is a direction, not a strict pixel-perfect layout.

Use whitespace and visual balance.

---

# Header

Create a minimal header:

```text
WEATHER / NOW
```

Optional small metadata:

```text
LIVE CONDITIONS
```

or current date/time.

Keep the header understated.

---

# Search Area

The search area is the main interaction.

Input:

```text
Search any city...
```

Requirements:

- large enough to be comfortable
- clean black surface
- subtle border
- lime focus state
- rounded corners should be restrained
- Enter submits the search
- button works
- loading state is visible

Button:

```text
CHECK →
```

or:

```text
SEARCH →
```

Avoid giant pill-shaped buttons.

---

# Loading State

When a request is being made:

Show a subtle loading state.

For example:

```text
FETCHING WEATHER...
```

Use a small animated indicator.

Do NOT freeze the UI.

---

# Weather Result

Prioritize information in this order:

### 1. Location

```text
RIGA, LATVIA
```

### 2. Temperature

```text
14°
```

This should be the visual focal point.

### 3. Condition

```text
PARTLY CLOUDY
```

### 4. Supporting metrics

```text
HUMIDITY       72%
FEELS LIKE     13°
WIND           12 KM/H
```

Optional:

```text
TIMEZONE       EUROPE/RIGA
```

---

# Weather Icon / Visual

If an icon is used, keep it minimal.

Do NOT use huge cartoon clouds.

Possible visual directions:

- minimalist line icon
- CSS-based weather indicator
- small monochrome icon
- subtle animated atmospheric element

The icon must never overpower the temperature.

---

# Day / Night

Use the API's `is_day` value.

You can subtly change the presentation:

```text
DAY
```

or:

```text
NIGHT
```

Do not completely redesign the page based on this value.

Keep the overall black/lime theme consistent.

---

# Error UI

Errors should appear inside the page rather than using browser alerts.

Example:

```text
CITY NOT FOUND

We couldn't find that location.
Try searching for another city.
```

Style the error state cleanly.

No red error explosion or giant warning banners.

---

# Animations

Animations should be subtle and fast.

Use:

- fade-in
- slide-up
- hover transitions
- focus transitions
- loading animation

Avoid:

- excessive bouncing
- spinning cards
- huge transitions
- parallax
- distracting particles

The experience should feel responsive and premium.

---

# Responsive Design

The website must work on:

- desktop
- laptop
- tablet
- mobile

On mobile:

- reduce page padding
- stack weather metrics
- make search full width
- keep temperature large
- prevent horizontal overflow
- maintain comfortable touch targets

Example mobile arrangement:

```text
WEATHER / NOW

SEARCH ANY CITY...

RIGA, LATVIA

14°
PARTLY CLOUDY

HUMIDITY
72%

FEELS LIKE
13°

WIND
12 KM/H
```

---

# JavaScript

Use vanilla JavaScript.

Responsibilities:

- read city input
- submit search
- call `/api/weather`
- handle loading
- parse JSON
- update the DOM
- display errors
- support Enter key
- prevent duplicate submissions while loading

Do not put API keys or server-side logic in JavaScript.

---

# Accessibility

Include:

- proper `<label>` for the search field
- keyboard navigation
- visible focus states
- semantic HTML
- sufficient text contrast
- descriptive button text
- accessible error messages

Use `aria-live` where appropriate for dynamic weather/error output.

---

# Performance

Keep the website lightweight.

Avoid unnecessary libraries.

Do not load:

- huge JavaScript frameworks
- huge animation libraries
- unnecessary icon libraries
- unnecessary fonts

The page should feel fast.

---

# Security

Never trust raw user input.

Always use `requests` query parameters.

Do not expose:

- API credentials
- server environment variables
- Python stack traces
- internal server details

Escape or safely insert dynamic values into the DOM.

---

# requirements.txt

Use:

```text
Flask
requests
gunicorn
```

`gunicorn` is useful for production deployment.

---

# .gitignore

Use:

```text
__pycache__/
*.py[cod]
.venv/
venv/
env/
.env
.vscode/
.idea/
```

Never commit:

```text
.env
```

or secret API keys.

---

# README.md

The README must include:

## Project

Short explanation of the weather website.

## Features

Mention:

- city search
- live weather
- temperature
- humidity
- feels-like temperature
- wind speed
- weather conditions
- error handling
- responsive UI

## Technologies

```text
Python
Flask
Requests
HTML
CSS
JavaScript
Open-Meteo API
```

## How It Works

Explain:

```text
User enters city
        ↓
JavaScript sends request
        ↓
Flask backend
        ↓
Open-Meteo Geocoding
        ↓
Latitude + Longitude
        ↓
Open-Meteo Weather API
        ↓
JSON response
        ↓
Flask normalizes data
        ↓
Website displays weather
```

## Installation

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python app.py
```

Then open the local address shown by Flask.

---

# GitHub Presentation

The repository should look professional.

Recommended files:

```text
weather-app/
├── app.py
├── requirements.txt
├── README.md
├── SKILLS.md
├── .gitignore
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

Do not upload:

- `venv/`
- `__pycache__/`
- `.pyc`
- `.env`
- unnecessary screenshots
- unused assets
- random generated files

---

# Code Quality

The project should be:

- beginner-friendly
- readable
- modular
- properly named
- easy to explain
- PEP 8-ish
- reasonably commented
- free of unnecessary dependencies

Avoid over-engineering.

Do not create dozens of files for a simple project.

---

# Final Visual Quality Bar

The final website should feel like:

> **A real premium weather product built with Python.**

Not:

> **A Python assignment wrapped in HTML.**

The design should have the same recognizable DNA as the previous password-generator website:

- black background
- lime accent
- strong modern typography
- oversized key information
- minimal borders
- clean spacing
- subtle glow
- restrained rounded corners
- premium editorial composition
- smooth but subtle motion

The most important visual element is the current temperature.

The interface should immediately communicate:

```text
WEATHER / NOW
```

followed by:

```text
CITY
TEMPERATURE
CONDITION
```

and then supporting data.

Keep the entire experience minimal, sharp, modern, and aesthetic.
