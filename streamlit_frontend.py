# streamlit.py

import re
import requests
import streamlit as st

# ———————— Configuration ————————
USER_AGENT    = "weather-app-streamlit/1.0 (khushidesai.ai@gmail.com)"
API_BASE      = "http://localhost:8000"
API_LOCATIONS = f"{API_BASE}/locations/"

# ———————— Helper functions ————————
def geocode(address: str) -> tuple[float, float]:
    resp = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": address, "format": "json", "limit": 1},
        headers={"User-Agent": USER_AGENT},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError(f"No location found for '{address}'")
    return float(data[0]["lat"]), float(data[0]["lon"])

def reverse_geocode(lat: float, lon: float) -> str:
    try:
        rev = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        rev.raise_for_status()
        return rev.json().get("display_name", f"{lat:.4f}, {lon:.4f}")
    except:
        return f"{lat:.4f}, {lon:.4f}"

def parse_input(inp: str) -> tuple[float, float]:
    m = re.match(r"\s*([-+]?\d+(\.\d+)?)\s*,\s*([-+]?\d+(\.\d+)?)\s*$", inp)
    if m:
        return float(m.group(1)), float(m.group(3))
    return geocode(inp)

def fetch_current(lat: float, lon: float) -> dict:
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": lat, "longitude": lon, "current_weather": True, "timezone": "auto"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["current_weather"]

def fetch_5day(lat: float, lon: float) -> list[dict]:
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,weathercode",
            "forecast_days": 5,
            "timezone": "auto",
        },
        timeout=10,
    )
    r.raise_for_status()
    daily = r.json()["daily"]
    return [
        {
            "date":      daily["time"][i],
            "temp_max":  daily["temperature_2m_max"][i],
            "temp_min":  daily["temperature_2m_min"][i],
            "weathercode": daily["weathercode"][i],
        }
        for i in range(len(daily["time"]))
    ]

# ———————— UI ————————
st.set_page_config(page_title="Weather & Favorites", layout="wide")
st.title("🌦️ Weather Explorer & Favorites")
st.markdown("_Developed by Khushi Desai_")

if st.button("ℹ️ Info"):
    st.info(
        "**Product Manager Accelerator** is our LinkedIn page where we empower aspiring product managers through hands-on training, mentorship, and community support.  \n"
        "🔗 [Visit on LinkedIn]"
        "(https://www.linkedin.com/school/pmaccelerator/)"
    )

col1, col2 = st.columns(2)

# — Favorites CRUD —
with col1:
    st.header("⭐ Favorites")

    # Add new favorite
    with st.form(key="form_add"):
        addr_input  = st.text_input("Location (name or coords)")
        alias_input = st.text_input("Friendly name (optional)")
        add_sub     = st.form_submit_button("Add to Favorites")
        if add_sub:
            try:
                lat, lon = parse_input(addr_input)
                name     = alias_input.strip() or reverse_geocode(lat, lon)
                payload  = {"name": name, "latitude": lat, "longitude": lon}
                resp     = requests.post(API_LOCATIONS, json=payload)
                resp.raise_for_status()
                st.success("✅ Saved!")
            except Exception as e:
                st.error(f"Error adding favorite: {e}")

    # Fetch updated favorites
    try:
        favorites = requests.get(API_LOCATIONS).json()
    except Exception as e:
        st.error(f"Could not load favorites: {e}")
        favorites = []

    # Display each favorite
    for fav in favorites:
        lat_lon_str = f"{fav['latitude']:.4f}, {fav['longitude']:.4f}"
        st.subheader(fav["name"])         # show saved name
        st.caption(lat_lon_str)           # coords as caption

        # Edit expander
        with st.expander("✏️ Edit this favorite"):
            with st.form(key=f"form_edit_{fav['id']}"):
                new_name   = st.text_input("New name (optional)", value=fav["name"])
                new_coords = st.text_input("New coords (lat,lon)", value=lat_lon_str)
                edit_sub   = st.form_submit_button("Save changes")
                if edit_sub:
                    try:
                        lat, lon = parse_input(new_coords)
                        name     = new_name.strip() or reverse_geocode(lat, lon)
                        payload  = {"name": name, "latitude": lat, "longitude": lon}
                        r        = requests.put(f"{API_LOCATIONS}{fav['id']}", json=payload)
                        r.raise_for_status()
                        st.success("✅ Updated!")
                    except Exception as e:
                        st.error(f"Error updating favorite: {e}")

        # Delete button
        if st.button("🗑️ Delete", key=f"del{fav['id']}"):
            try:
                r = requests.delete(f"{API_LOCATIONS}{fav['id']}")
                r.raise_for_status()
                st.success("✅ Deleted!")
            except Exception as e:
                st.error(f"Error deleting favorite: {e}")

# — Manual Lookup —
with col2:
    st.header("🔍 Manual Lookup")
    lookup = st.text_input("Enter a location", key="manual")
    if st.button("Get Weather"):
        if not lookup:
            st.warning("Please enter a location.")
        else:
            try:
                lat, lon = parse_input(lookup)
                st.session_state.show = {
                    "name": reverse_geocode(lat, lon),
                    "latitude": lat,
                    "longitude": lon,
                }
                st.session_state.current  = fetch_current(lat, lon)
                st.session_state.forecast = fetch_5day(lat, lon)
            except Exception as e:
                st.error(f"Error: {e}")

# — Display Weather —
if st.session_state.get("show"):
    fav      = st.session_state.show
    current  = st.session_state.current
    forecast = st.session_state.forecast

    st.markdown("---")
    st.subheader(f"Weather for **{fav['name']}**")
    c1, c2, c3 = st.columns(3)
    c1.metric("Temperature (°C)", current.get("temperature", "—"))
    c2.metric("Wind Speed (km/h)", current.get("windspeed", "—"))
    c3.metric("Wind Dir (°)", current.get("winddirection","—"))
    st.write(f"**Time:** {current.get('time','—')} UTC")

    st.subheader("5-Day Forecast")
    for d in forecast:
        st.write(f"**{d['date']}**: High {d['temp_max']}°C | Low {d['temp_min']}°C | Code {d['weathercode']}")

st.markdown("---")
st.markdown("Built with ❤️ using Streamlit")
