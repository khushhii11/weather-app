# weather/weather_app.py

import logging
from typing import List, Dict

import requests

# ———————— Configuration ————————
logger = logging.getLogger(__name__)
BASE_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 10  # seconds to wait for the service
SESSION = requests.Session()


def fetch_current(lat: float, lon: float) -> Dict:
    """
    Fetch the current weather for a given latitude & longitude.

    Args:
        lat: Latitude of the location.
        lon: Longitude of the location.

    Returns:
        A dict containing the 'current_weather' data from Open-Meteo.

    Raises:
        ConnectionError: On network issues or non-2xx HTTP status.
        ValueError: If the response is missing or malformed.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "auto",
    }
    try:
        resp = SESSION.get(BASE_URL, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.exception("Error fetching current weather")
        raise ConnectionError(f"Error fetching current weather: {e}") from e
    except ValueError as e:
        logger.exception("Invalid JSON received for current weather")
        raise ValueError("Received invalid JSON for current weather") from e

    if not isinstance(data, dict) or "current_weather" not in data:
        raise ValueError("Response JSON is missing 'current_weather'")

    return data["current_weather"]


def fetch_5day(lat: float, lon: float) -> List[Dict]:
    """
    Fetch a 5-day daily forecast for a given latitude & longitude.

    Each day's record includes:
      - date (ISO string)
      - temp_max (float)
      - temp_min (float)
      - weathercode (int)

    Args:
        lat: Latitude of the location.
        lon: Longitude of the location.

    Returns:
        A list of 5 dicts, one per day.

    Raises:
        ConnectionError: On network issues or non-2xx HTTP status.
        ValueError: If the response is missing or malformed.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,weathercode",
        "timezone": "auto",
        "forecast_days": 5,
    }
    try:
        resp = SESSION.get(BASE_URL, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as e:
        logger.exception("Error fetching 5-day forecast")
        raise ConnectionError(f"Error fetching 5-day forecast: {e}") from e
    except ValueError as e:
        logger.exception("Invalid JSON received for 5-day forecast")
        raise ValueError("Received invalid JSON for 5-day forecast") from e

    daily = payload.get("daily")
    if not isinstance(daily, dict):
        raise ValueError("Response JSON is missing 'daily' forecast data")

    times       = daily.get("time", [])
    max_temps   = daily.get("temperature_2m_max", [])
    min_temps   = daily.get("temperature_2m_min", [])
    weathercodes= daily.get("weathercode", [])

    if not (len(times) == len(max_temps) == len(min_temps) == len(weathercodes)):
        raise ValueError("Forecast arrays are of unequal length")

    forecast: List[Dict] = []
    for date, tmax, tmin, code in zip(times, max_temps, min_temps, weathercodes):
        forecast.append({
            "date":      date,
            "temp_max":  tmax,
            "temp_min":  tmin,
            "weathercode": code,
        })

    return forecast
