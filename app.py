import requests

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Weather Dashboard", page_icon="🌤️", layout="wide")


def html(text):
    # Remove line breaks and extra spaces so Streamlit always reads this as HTML
    st.markdown(" ".join(text.split()), unsafe_allow_html=True)


# ---------- Styling (works on laptop and phone) ----------
html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
    .stApp { background: #F4F6F9; color: #1F2A37; }
    h1, h2, h3, h4, p, label, span { color: #1F2A37; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 1.5rem; max-width: 1200px; }

    .page-title { font-size: 1.6rem; font-weight: 700; margin: 0; }
    .page-sub { color: #6B7787; font-size: 0.9rem; margin-bottom: 0.8rem; }

    .hero { background: linear-gradient(135deg, #12355B 0%, #1F5E99 100%);
        border-radius: 16px; padding: 22px 28px; margin-bottom: 14px;
        display: flex; flex-wrap: wrap; justify-content: space-between;
        align-items: center; gap: 12px; }
    .hero * { color: #FFFFFF !important; }
    .hero .place { font-size: 0.95rem; font-weight: 500; opacity: 0.9; }
    .hero .temp { font-size: 3.6rem; font-weight: 700; line-height: 1.1; }
    .hero .cond { font-size: 1.15rem; font-weight: 500; }
    .hero .hl { font-size: 0.95rem; margin-top: 6px; }
    .hero svg { width: 170px; height: auto; }

    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 12px; margin-bottom: 14px; }
    .mcard { background: #FFFFFF; border: 1px solid #E3E8EF; border-radius: 12px;
        padding: 12px 16px; }
    .mcard .ml { color: #6B7787; font-size: 0.85rem; font-weight: 500; }
    .mcard .mv { font-size: 1.45rem; font-weight: 700; color: #1F2A37; }

    [data-testid="stVerticalBlockBorderWrapper"] { background: #FFFFFF;
        border-radius: 12px; border-color: #E3E8EF; }
    .section { font-size: 1.1rem; font-weight: 600; margin: 20px 0 10px 0; }
    .chart-title { font-size: 0.9rem; font-weight: 600; margin-bottom: 2px; }

    .days { display: grid; grid-template-columns: repeat(auto-fit, minmax(92px, 1fr)); gap: 10px; }
    .daycard { background: #FFFFFF; border: 1px solid #E3E8EF; border-radius: 12px;
        padding: 10px 4px; text-align: center; line-height: 1.5; }
    .daycard .d { font-weight: 600; font-size: 0.85rem; }
    .daycard .i { font-size: 1.8rem; }
    .daycard .c { color: #6B7787; font-size: 0.72rem; min-height: 2.2em; }
    .daycard .hi { color: #D1495B; font-weight: 700; font-size: 1.05rem; }
    .daycard .lo { color: #2F6DB5; font-weight: 500; }
    .daycard .rn { color: #6B7787; font-size: 0.75rem; }

    .footer-note { color: #6B7787; font-size: 0.8rem; text-align: center; margin-top: 24px; }

    @media (max-width: 640px) {
        .block-container { padding: 1rem 0.8rem; }
        .hero { padding: 16px 18px; }
        .hero .temp { font-size: 2.8rem; }
        .hero svg { width: 110px; }
        .page-title { font-size: 1.3rem; }
    }
    </style>
    """
)

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

ICONS = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌫️", 48: "🌫️",
    51: "🌦️", 53: "🌦️", 55: "🌦️", 56: "🌧️", 57: "🌧️",
    61: "🌧️", 63: "🌧️", 65: "🌧️", 66: "🌧️", 67: "🌧️",
    71: "🌨️", 73: "🌨️", 75: "❄️", 77: "❄️",
    80: "🌦️", 81: "🌧️", 82: "⛈️", 85: "🌨️", 86: "🌨️",
    95: "⛈️", 96: "⛈️", 99: "⛈️",
}


def describe(code):
    return WEATHER_CODES.get(code, "Unknown")


def icon(code):
    return ICONS.get(code, "🌡️")


def weather_svg(code):
    # A small drawn picture for the top card (no internet image needed)
    sun = "".join(
        f'<line x1="60" y1="50" x2="{60 + 34 * c}" y2="{50 + 34 * s}" stroke="#FFD166" stroke-width="5" stroke-linecap="round"/>'
        for c, s in [(1, 0), (0.71, 0.71), (0, 1), (-0.71, 0.71), (-1, 0), (-0.71, -0.71), (0, -1), (0.71, -0.71)]
    )
    sun += '<circle cx="60" cy="50" r="20" fill="#FFD166"/>'
    small_sun = '<circle cx="42" cy="38" r="18" fill="#FFD166"/>'
    cloud = ('<circle cx="42" cy="62" r="15" fill="#EAF1F8"/><circle cx="62" cy="52" r="20" fill="#EAF1F8"/>'
             '<circle cx="82" cy="63" r="14" fill="#EAF1F8"/><rect x="42" y="62" width="40" height="15" fill="#EAF1F8"/>')
    drops = "".join(
        f'<line x1="{x}" y1="84" x2="{x - 4}" y2="96" stroke="#7CC4FF" stroke-width="4" stroke-linecap="round"/>'
        for x in (48, 62, 76)
    )
    flakes = "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#FFFFFF"/>' for x, y in ((48, 88), (62, 94), (76, 88)))
    bolt = '<polygon points="64,78 54,92 62,92 58,102 74,86 65,86 70,78" fill="#FFD166"/>'

    if code in (0, 1):
        body = sun
    elif code == 2:
        body = small_sun + cloud
    elif code in (3, 45, 48):
        body = cloud
    elif code in (71, 73, 75, 77, 85, 86):
        body = cloud + flakes
    elif code in (95, 96, 99):
        body = cloud + bolt
    else:
        body = cloud + drops
    return f'<svg viewBox="0 0 120 105" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


@st.cache_data(ttl=600)
def find_city(name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    response = requests.get(url, params={"name": name, "count": 1}, timeout=10)
    response.raise_for_status()
    results = response.json().get("results")
    if results:
        return results[0]
    return None


@st.cache_data(ttl=600)
def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,precipitation,weather_code",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset",
        "timezone": "auto",
        "forecast_days": 7,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


# ---------- Header and search ----------
html('<p class="page-title">🌤️ Weather Dashboard</p>')
html('<p class="page-sub">Live data from Open-Meteo</p>')

search_col, button_col = st.columns([4, 1])
city = search_col.text_input("🔍 City name", "Islamabad")
button_col.write("")
button_col.write("")
if button_col.button("🔄 Update"):
    st.cache_data.clear()
    st.rerun()

# ---------- Get the data ----------
try:
    place = find_city(city)
    if place is None:
        st.error("City not found. Please check the spelling.")
        st.stop()
    data = get_weather(place["latitude"], place["longitude"])
except requests.RequestException:
    st.error("Could not reach the weather service. Check your internet connection.")
    st.stop()

now = data["current"]
daily_raw = data["daily"]
code_now = now["weather_code"]
temp = now["temperature_2m"]
rain_chance = daily_raw["precipitation_probability_max"][0]
rain_text = f"{rain_chance} %" if rain_chance is not None else "-"
sunrise = pd.to_datetime(daily_raw["sunrise"][0]).strftime("%H:%M")
sunset = pd.to_datetime(daily_raw["sunset"][0]).strftime("%H:%M")

# ---------- Top card with picture ----------
today = pd.to_datetime(now["time"]).strftime("%A, %d %B %Y")
html(
    f"""
    <div class="hero">
        <div>
            <div class="place">📍 {place['name']}, {place.get('country', '')} &nbsp;|&nbsp; {today}</div>
            <div class="temp">{temp} °C</div>
            <div class="cond">{icon(code_now)} {describe(code_now)}</div>
            <div class="hl">⬆️ {daily_raw['temperature_2m_max'][0]}° &nbsp;&nbsp; ⬇️ {daily_raw['temperature_2m_min'][0]}°</div>
        </div>
        <div>{weather_svg(code_now)}</div>
    </div>
    """
)

# ---------- Current weather cards ----------
html(
    f"""
    <div class="grid">
        <div class="mcard"><div class="ml">💧 Humidity</div><div class="mv">{now['relative_humidity_2m']} %</div></div>
        <div class="mcard"><div class="ml">💨 Wind speed</div><div class="mv">{now['wind_speed_10m']} km/h</div></div>
        <div class="mcard"><div class="ml">🌧️ Rain now</div><div class="mv">{now['precipitation']} mm</div></div>
        <div class="mcard"><div class="ml">☔ Rain chance today</div><div class="mv">{rain_text}</div></div>
        <div class="mcard"><div class="ml">🌡️ Feels like</div><div class="mv">{now['apparent_temperature']} °C</div></div>
        <div class="mcard"><div class="ml">🌅 Sunrise / 🌇 Sunset</div><div class="mv">{sunrise} / {sunset}</div></div>
    </div>
    """
)

# ---------- Recommendation ----------
if rain_chance is not None and rain_chance > 60:
    st.warning("☔ High chance of rain today. Take an umbrella.")
elif temp > 35:
    st.warning("🥵 Very hot. Stay hydrated and avoid midday sun.")
elif temp < 10:
    st.info("🧥 Cold day. Wear a jacket.")
else:
    st.success("😎 Good day for outdoor activity.")

# ---------- 7-day forecast cards ----------
html('<div class="section">📅 7-day forecast</div>')
cards = ""
for i in range(len(daily_raw["time"])):
    day_name = pd.to_datetime(daily_raw["time"][i]).strftime("%a %d")
    rain_pct = daily_raw["precipitation_probability_max"][i]
    rain_pct = rain_pct if rain_pct is not None else "-"
    cards += (
        f'<div class="daycard">'
        f'<div class="d">{day_name}</div>'
        f'<div class="i">{icon(daily_raw["weather_code"][i])}</div>'
        f'<div class="c">{describe(daily_raw["weather_code"][i])}</div>'
        f'<div class="hi">{daily_raw["temperature_2m_max"][i]}°</div>'
        f'<div class="lo">{daily_raw["temperature_2m_min"][i]}°</div>'
        f'<div class="rn">🌧️ {rain_pct}%</div>'
        f'</div>'
    )
html(f'<div class="days">{cards}</div>')

# ---------- Next 24 hours: four small charts in a 2 x 2 grid ----------
html('<div class="section">⏱️ Next 24 hours</div>')
hourly = pd.DataFrame(data["hourly"])
hourly["time"] = pd.to_datetime(hourly["time"])
hourly = hourly.set_index("time").head(24)

left, right = st.columns(2)
with left:
    with st.container(border=True):
        html('<div class="chart-title">🌡️ Temperature (°C)</div>')
        st.line_chart(hourly["temperature_2m"], color="#D1495B", height=150)
    with st.container(border=True):
        html('<div class="chart-title">💧 Humidity (%)</div>')
        st.line_chart(hourly["relative_humidity_2m"], color="#2A9D8F", height=150)
with right:
    with st.container(border=True):
        html('<div class="chart-title">🌧️ Rainfall (mm per hour)</div>')
        st.bar_chart(hourly["precipitation"], color="#2F6DB5", height=150)
    with st.container(border=True):
        html('<div class="chart-title">💨 Wind speed (km/h)</div>')
        st.line_chart(hourly["wind_speed_10m"], color="#6C757D", height=150)

# ---------- 7-day chart and table ----------
daily = pd.DataFrame(data["daily"])
daily["time"] = pd.to_datetime(daily["time"])
daily = daily.set_index("time")

html('<div class="section">📊 7-day details</div>')
chart_col, table_col = st.columns(2)
with chart_col:
    with st.container(border=True):
        html('<div class="chart-title">📈 Highest and lowest temperature (°C)</div>')
        st.line_chart(
            daily[["temperature_2m_max", "temperature_2m_min"]],
            color=["#D1495B", "#2F6DB5"],
            height=200,
        )
with table_col:
    forecast = pd.DataFrame({
        "Condition": daily["weather_code"].map(describe),
        "High (°C)": daily["temperature_2m_max"],
        "Low (°C)": daily["temperature_2m_min"],
        "Rain chance (%)": daily["precipitation_probability_max"],
        "Rain (mm)": daily["precipitation_sum"],
        "Sunrise": pd.to_datetime(daily["sunrise"]).dt.strftime("%H:%M"),
        "Sunset": pd.to_datetime(daily["sunset"]).dt.strftime("%H:%M"),
    })
    forecast.index = forecast.index.strftime("%a %d %b")
    st.dataframe(forecast, use_container_width=True, height=260)

html('<div class="footer-note">Data source: Open-Meteo.com | Built with Python, Streamlit and pandas</div>')
    
    


