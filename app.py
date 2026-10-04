import requests

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Weather Dashboard", layout="wide")
st.title("Weather Dashboard")

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Fog (rime)",
    51: "Light drizzle", 53: "Drizzle", 55: "Dense drizzle",
    56: "Freezing drizzle", 57: "Freezing drizzle",
    61: "Slight rain", 63: "Rain", 65: "Heavy rain",
    66: "Freezing rain", 67: "Freezing rain",
    71: "Slight snow", 73: "Snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Rain showers", 81: "Rain showers", 82: "Violent rain showers",
    85: "Snow showers", 86: "Snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with hail",
}


def describe(code):
    return WEATHER_CODES.get(code, "Unknown")


def find_city(name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    response = requests.get(url, params={"name": name, "count": 1}, timeout=10)
    response.raise_for_status()
    results = response.json().get("results")
    if results:
        return results[0]
    return None


def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 7,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


city = st.sidebar.text_input("City name", "Islamabad")

if st.sidebar.button("Update weather"):
    st.cache_data.clear()
    st.rerun()

try:
    place = find_city(city)
    if place is None:
        st.error("City not found. Please check the spelling.")
        st.stop()
    data = get_weather(place["latitude"], place["longitude"])
except requests.RequestException:
    st.error("Could not reach the weather service. Check your internet connection.")
    st.stop()

st.subheader(f"{place['name']}, {place.get('country', '')}")

now = data["current"]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Condition", describe(now["weather_code"]))
c2.metric("Temperature", f"{now['temperature_2m']} °C")
c3.metric("Humidity", f"{now['relative_humidity_2m']} %")
c4.metric("Wind speed", f"{now['wind_speed_10m']} km/h")
c5.metric("Rain now", f"{now['precipitation']} mm")

st.subheader("Recommendation")
rain_chance = data["daily"]["precipitation_probability_max"][0]
temp = now["temperature_2m"]

if rain_chance is not None and rain_chance > 60:
    st.warning("High chance of rain today. Take an umbrella.")
elif temp > 35:
    st.warning("Very hot. Stay hydrated and avoid midday sun.")
elif temp < 10:
    st.info("Cold day. Wear a jacket.")
else:
    st.success("Good day for outdoor activity.")

hourly = pd.DataFrame(data["hourly"])
hourly["time"] = pd.to_datetime(hourly["time"])
hourly = hourly.set_index("time")

left, right = st.columns(2)

with left:
    st.subheader("Temperature (°C)")
    st.line_chart(hourly["temperature_2m"])
    st.subheader("Rainfall (mm per hour)")
    st.bar_chart(hourly["precipitation"])

with right:
    st.subheader("Humidity (%)")
    st.line_chart(hourly["relative_humidity_2m"])
    st.subheader("Wind speed (km/h)")
    st.line_chart(hourly["wind_speed_10m"])
    daily = pd.DataFrame(data["daily"])
daily["time"] = pd.to_datetime(daily["time"])
daily = daily.set_index("time")

st.subheader("7-day forecast: highest and lowest temperature (°C)")
st.line_chart(daily[["temperature_2m_max", "temperature_2m_min"]])

st.subheader("7-day forecast table")
forecast = pd.DataFrame({
    "Condition": daily["weather_code"].map(describe),
    "Highest (°C)": daily["temperature_2m_max"],
    "Lowest (°C)": daily["temperature_2m_min"],
    "Rain chance (%)": daily["precipitation_probability_max"],
    "Rain total (mm)": daily["precipitation_sum"],
})
forecast.index = forecast.index.strftime("%a %d %b")
st.dataframe(forecast)