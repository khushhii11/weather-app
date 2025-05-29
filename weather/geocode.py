# weather/geocode.py

import os
import logging
from typing import Tuple

import requests
from dotenv import load_dotenv

# ———————— Configuration ————————
load_dotenv()  # read from .env at project root

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
TIMEOUT = 10  # seconds to wait for the geocoding service
SESSION = requests.Session()
logger = logging.getLogger(__name__)

USER_AGENT_TEMPLATE = "weather-app-example/1.0 ({email})"


def geocode(address: str) -> Tuple[float, float]:
    """
    Convert an address (string) to latitude and longitude via Nominatim.

    Requires:
        - GEOCODER_EMAIL set in your environment or .env

    Args:
        address: Free-form location (e.g. "Dallas, TX" or "75001").

    Returns:
        Tuple of (latitude, longitude) as floats.

    Raises:
        RuntimeError: If GEOCODER_EMAIL is not configured.
        ConnectionError: On network/HTTP errors.
        ValueError: If no results are found or response is malformed.
    """
    email = os.getenv("GEOCODER_EMAIL")
    if not email:
        logger.error("GEOCODER_EMAIL is missing; cannot geocode.")
        raise RuntimeError(
            "Missing GEOCODER_EMAIL environment variable. "
            "Add it to your .env or OS environment."
        )

    headers = {"User-Agent": USER_AGENT_TEMPLATE.format(email=email)}
    params = {"q": address, "format": "json", "limit": 1}

    try:
        resp = SESSION.get(
            NOMINATIM_URL, params=params, headers=headers, timeout=TIMEOUT
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.exception("HTTP error during geocoding request")
        raise ConnectionError(f"Error contacting geocoding service: {e}") from e

    try:
        data = resp.json()
    except ValueError as e:
        logger.exception("Invalid JSON received from geocoding service")
        raise ValueError("Received malformed JSON from geocoding service") from e

    if not isinstance(data, list) or not data:
        raise ValueError(f"No location found for '{address}'")

    location = data[0]
    try:
        lat = float(location["lat"])
        lon = float(location["lon"])
    except (KeyError, TypeError, ValueError) as e:
        logger.exception("Missing or invalid lat/lon in geocoding response")
        raise ValueError("Latitude or longitude missing in response") from e

    return lat, lon
