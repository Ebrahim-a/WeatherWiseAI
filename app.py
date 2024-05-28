import streamlit as st
import requests
import openai
import json
from openai import OpenAI
from datetime import datetime

#function to fetch

def get_weather_data(city, weather_api_key):
    base_url="http://api.openweathermap.org/data/2.5/weather?"
    complete_url= base_url + "appid=" + weather_api_key + "&q=" +city
    respone = requests.get(complete_url)
    return respone.json()

def generate_weather_description(data, openai_api_key):
    openai.api_key=openai_api_key

    try:
        temperature = data['main']['temp'] - 273.15 #convert Kevl to celsius
        description = data['weather'][0]['description']
        prompt =f"The Current weather in your city is {description} with a temperature of {temperature:.1f}°C. What is good to do in this Weather in less than 3 sentence."

        response = openai.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt =prompt,
            max_tokens=60
        )

        return response.choices[0].text.strip()
    except Exception as e:
        return str(e)
    

def get_weekly_forecast(weather_api_key, lat, lon):
    base_url="http://api.openweathermap.org/data/2.5/"
    complete_url= f"{base_url}forecast?lat={lat}&lon={lon}&appid={weather_api_key}"
    respone = requests.get(complete_url)
    return respone.json()

def display_weekly_forecast(data):
    try:
        st.write("======================================================")
        st.write("### Weekly Weather Forecast")
        displayed_dates=set()

        c1,c2,c3,c4=st.columns(4)
        with c1:
            st.metric("", "Day")
        with c2:
            st.metric("", "Desc")
        with c3:
            st.metric("", "Min_temp")
        with c4:
            st.metric("", "Max_temp")

        for day in data['list']:
            date = datetime.fromtimestamp(day['dt']).strftime('%A, %B %d')
            if date not in displayed_dates:
                displayed_dates.add(date)

                min_temp= day['main']['temp_min'] - 273.15
                max_temp= day['main']['temp_max'] - 273.15
                description = day['weather'][0]['description']

                with c1:
                    st.write(f"{date}")
                with c2:
                    st.write(f"{description.capitalize()}")
                with c3:
                    st.write(f"{min_temp:.1f}")
                with c4:
                    st.write(f"{max_temp:.1f}")

    except Exception as e:
        st.error("Error displaying weekly" + str(e))


def main():
    st.sidebar.title("Weather forecasting with LLM")
    city = st.sidebar.text_input("Enter city name", "London")

    #API Keys
    weather_api_key=""
    openai_api_key=""

    submit= st.sidebar.button("Get Weather")

    if submit:
        st.title("Weather Updates for " + city + " is:")
        with st.spinner('Fetching Weather Data...'):
            weather_data= get_weather_data(city, weather_api_key)
            print(weather_data)

            if weather_data.get("cod") != 404:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Temperature ", f"{weather_data['main']['temp'] - 273.15:.2f} °C")
                    st.metric("Humidity ", f"{weather_data['main']['humidity']}%")
                with col2:
                    st.metric("Pressure ", f"{weather_data['main']['pressure']} hPa")
                    st.metric("Wind Speed ", f"{weather_data['wind']['speed']}m/s")

                lat = weather_data['coord']['lat']    
                lon = weather_data['coord']['lon']  

                weather_description = generate_weather_description(weather_data,openai_api_key)
                st.write(weather_description)

                #To call weekly
                forecast_date = get_weekly_forecast(weather_api_key, lat,lon)
                print(forecast_date)
                if forecast_date.get("cod") != 404:
                    display_weekly_forecast(forecast_date)
            else:
                st.error("City not found or an error Occurred!")

    
if __name__ == "__main__":
    main()