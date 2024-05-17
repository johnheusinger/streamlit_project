import streamlit as st
import requests
import pandas as pd
import numpy as np
import joblib

API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]

# Get place suggestions
def get_place_suggestions(input_text):
    url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input={input_text}&types=geocode&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        predictions = response.json().get('predictions', [])
        return [{'description': item['description'], 'place_id': item['place_id']} for item in predictions]
    else:
        return []

# Get place details to fetch GPS coordinates
def get_place_details(place_id):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json().get('result', {})
        location = result.get('geometry', {}).get('location', {})
        return location.get('lat'), location.get('lng')
    else:
        return None, None

def day_of_week_to_int(day_of_week):
    days = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }
    return days[day_of_week]

def constructInputdf(hour:int = 14,
                     day_of_week:int= 3,
                     gps_distance:float= 5.2,
                     pickup_latitude:float= 40.748817,
                     pickup_longitude:float= -73.985428):
    # Construct the DataFrame row

    # Column names
    columns = ['hour', 'day_of_week', 'gps_distance', 'pickup_latitude', 'pickup_longitude']

    # Construct the DataFrame row
    data_row = pd.DataFrame([[hour, day_of_week, gps_distance, pickup_latitude, pickup_longitude]], columns=columns)

    return data_row

def predict_tip_amount(hour:int = 14,
                       day_of_week:int= 3,
                       gps_distance:float= 5.2,
                       pickup_latitude:float= 40.748817,
                       pickup_longitude:float= -73.985428):
    # Load the model
    model = joblib.load('./outputs/models/tip_amount_model.pkl')
    

    input_X = constructInputdf(hour,
                               day_of_week,
                               gps_distance,
                               pickup_latitude,
                               pickup_longitude)

    # Ensure input_X is a DataFrame
    if not isinstance(input_X, pd.DataFrame):
        input_X = pd.DataFrame(input_X)
    
    # Run the prediction
    predictions = model.predict(input_X)
    
    return predictions