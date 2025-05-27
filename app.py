# weather_dashboard.py

import requests
import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import folium_static
import json

# ----------- Weather API Configuration -----------
API_KEY = "88a64324cf5421e8f91232ed276fd873"  # Replace with your OpenWeather API key
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city, state=None, country="IN"):
    """Fetches current weather data for any given city and state."""
    location_query = f"{city},{country}" if not state else f"{city},{state},{country}"
    url = f"{BASE_URL}?q={location_query}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        weather_info = {
            "city": data.get("name", city),
            "state": state if state else "N/A",
            "country": country,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": data["main"].get("temp", "N/A"),
            "humidity": data["main"].get("humidity", "N/A"),
            "wind_speed": data["wind"].get("speed", "N/A"),
            "pressure": data["main"].get("pressure", "N/A"),
            "weather_condition": data["weather"][0].get("main", "N/A"),
            "latitude": data["coord"].get("lat", "N/A"),
            "longitude": data["coord"].get("lon", "N/A"),
        }
        return weather_info

    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {e}")
        return None

# ----------- Streamlit Dashboard UI -----------

st.set_page_config(page_title="Weather Dashboard", layout="wide")
st.title("🌤️ Real-Time Weather Dashboard")

# Load state-city data
with open("data.json", "r") as f:
    state_city_data = json.load(f)

# UI for state and city selection
state_name = st.selectbox("🏙️ Select State", sorted(state_city_data.keys()))
city_list = state_city_data.get(state_name, [])
city_name = st.selectbox("🌆 Select City", city_list)

# Button to fetch weather
if st.button("🔍 Get Weather"):
    weather_info = get_weather(city_name, state_name)

    if weather_info:
        st.success("✅ Weather data retrieved!")

        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌡 Temperature", f"{weather_info['temperature']} °C")
        col2.metric("💧 Humidity", f"{weather_info['humidity']}%")
        col3.metric("🌬 Wind Speed", f"{weather_info['wind_speed']} m/s")
        col4.metric("📈 Pressure", f"{weather_info['pressure']} hPa")

        st.write(f"📍 Coordinates: {weather_info['latitude']}, {weather_info['longitude']}")
        st.write(f"🕒 Date/Time: {weather_info['date']}")
        st.write(f"🌥 Condition: {weather_info['weather_condition']}")

        # Map
        st.subheader("🗺️ Location Map")
        map = folium.Map(location=[weather_info['latitude'], weather_info['longitude']], zoom_start=10)
        folium.Marker(
            [weather_info['latitude'], weather_info['longitude']],
            popup=f"{city_name}",
            tooltip=weather_info['weather_condition']
        ).add_to(map)
        folium_static(map)

        # Simulated data
        st.subheader("📊 Simulated 10-Day Trends")
        df = pd.DataFrame({
            "Date": pd.date_range(end=pd.Timestamp.today(), periods=10),
            "Temperature": [weather_info["temperature"] + i for i in range(10)],
            "Humidity": [weather_info["humidity"] - i for i in range(10)],
            "Wind Speed": [weather_info["wind_speed"] + i * 0.2 for i in range(10)],
        })

        st.dataframe(df)

        # Line Plot
        for column, color in zip(["Temperature", "Humidity", "Wind Speed"], ["blue", "green", "red"]):
            st.subheader(f"📈 {column} Trend")
            fig, ax = plt.subplots(figsize=(8, 3))
            ax.plot(df["Date"], df[column], marker='o', color=color)
            ax.set_title(f"{column} Over 10 Days")
            ax.set_xlabel("Date")
            ax.set_ylabel(column)
            ax.grid(True)
            plt.xticks(rotation=45)
            fig.tight_layout()
            st.pyplot(fig)

        # Histogram
        for column, color in zip(["Temperature", "Humidity", "Wind Speed"], ["skyblue", "lightgreen", "salmon"]):
            st.subheader(f"📊 {column} Distribution")
            fig, ax = plt.subplots(figsize=(8, 3))
            sns.histplot(df[column], kde=True, color=color, ax=ax)
            ax.set_title(f"{column} Distribution")
            fig.tight_layout()
            st.pyplot(fig)

        # Bar Charts
        st.subheader("📊 Bar Charts")
        for column, color in zip(["Temperature", "Humidity", "Wind Speed"], ["orange", "teal", "purple"]):
            fig, ax = plt.subplots(figsize=(8, 3))
            ax.bar(df["Date"].dt.strftime('%b %d'), df[column], color=color)
            ax.set_title(f"{column} Bar Chart")
            plt.xticks(rotation=45)
            fig.tight_layout()
            st.pyplot(fig)

        # Scatter Plots
        st.subheader("🔵 Scatter Plots")
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.scatter(df["Temperature"], df["Humidity"], color='darkgreen')
        ax1.set_xlabel("Temperature (°C)")
        ax1.set_ylabel("Humidity (%)")
        ax1.set_title("Temperature vs Humidity")
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.scatter(df["Temperature"], df["Wind Speed"], color='darkred')
        ax2.set_xlabel("Temperature (°C)")
        ax2.set_ylabel("Wind Speed (m/s)")
        ax2.set_title("Temperature vs Wind Speed")
        st.pyplot(fig2)

        # Pair Plot
        st.subheader("🧭 Pair Plot (All Metrics)")
        pairplot_fig = sns.pairplot(df[["Temperature", "Humidity", "Wind Speed"]])
        st.pyplot(pairplot_fig)

        # Correlation Heatmap
        st.subheader("🔥 Correlation Heatmap")
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        sns.heatmap(df[["Temperature", "Humidity", "Wind Speed"]].corr(), annot=True, cmap="coolwarm", ax=ax3)
        ax3.set_title("Correlation Matrix")
        st.pyplot(fig3)

        # Box Plots
        st.subheader("📦 Box Plots (Distribution Spread)")
        fig4, ax4 = plt.subplots(figsize=(8, 4))
        sns.boxplot(data=df[["Temperature", "Humidity", "Wind Speed"]])
        ax4.set_title("Metric Variability")
        st.pyplot(fig4)

        # Area Chart
        st.subheader("🌄 Area Chart (Stacked Trends)")
        fig5, ax5 = plt.subplots(figsize=(8, 4))
        df_plot = df.set_index("Date")[["Temperature", "Humidity", "Wind Speed"]]
        df_plot.plot.area(ax=ax5, alpha=0.6)
        ax5.set_title("Weather Metrics Area Plot")
        plt.xticks(rotation=45)
        fig5.tight_layout()
        st.pyplot(fig5)

    else:
        st.error("❌ Failed to retrieve weather data. Check city/state or API key.")

