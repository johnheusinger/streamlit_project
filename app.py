import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from app.utils import get_place_suggestions, get_place_details, day_of_week_to_int, predict_tip_amount
from src.functions import make_prediction, load_model
import plotly.express as px
import plotly.graph_objects as go

tab1, tab2 = st.tabs(["📈 Exploration", "🗃 Prediction"])

# Fetch API key from Streamlit Secrets
API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]

### The Visualizations Tab 1

# The stuff under tab1.xyz are all exploration related UI eliments.
tab1.subheader("A tab with a chart")
df = pd.read_csv("outputs/csvdata/VisualizeLocations.csv")
# pickups = pd.read_csv("data/processed_data/PickupLocations.csv")
# dropoff = pd.read_csv("data/processed_data/DropoffLocations.csv")

df20 =  df.head(20000)
# pick_df20 =  pickups.head(20000)
# drop_df20 =  dropoff.head(20000)

tab1.map(df20, size=2, color='color')

# JFK trips code.

# Load data from file
data = pd.read_csv('outputs/csvdata/JFK_trips.csv')  # Load your dataset

# Extract hour and day of week from pickup_datetime
data['pickup_datetime'] = pd.to_datetime(data['pickup_datetime'])
data['hour'] = data['pickup_datetime'].dt.hour
data['day_of_week'] = data['pickup_datetime'].dt.dayofweek

# Group by day_of_week and hour
grouped_data = data.groupby(['day_of_week', 'hour']).agg({
    'trip_duration': ['mean', 'median', 'std'],
    'total_amount': ['mean', 'median', 'std']
}).reset_index()

# Rename columns for easier access
grouped_data.columns = ['day_of_week', 'hour', 'duration_mean', 'duration_median', 'duration_std', 'fare_mean', 'fare_median', 'fare_std']

# Streamlit app
tab1.title('Trip Duration and Fare Analysis')

# Add a slider for selecting hour of the day
selected_hour = tab1.slider('Select Hour of the Day', min_value=0, max_value=23, value=12, step=1)

# Filter data for the selected hour of the day
filtered_data = grouped_data[grouped_data['hour'] == selected_hour]

# Plotting with Plotly
fig = go.Figure()

# Add mean line with error bars
fig.add_trace(go.Scatter(
    x=filtered_data['day_of_week'],
    y=filtered_data['duration_mean'],
    mode='lines+markers',
    name='Mean',
    error_y=dict(type='data', array=filtered_data['duration_std'], visible=True),
    line=dict(color='royalblue')
))

# Add median line
fig.add_trace(go.Scatter(
    x=filtered_data['day_of_week'],
    y=filtered_data['duration_median'],
    mode='lines+markers',
    name='Median',
    line=dict(color='orange')
))

# Update layout for dark theme
fig.update_layout(
    title=f'Trip Duration Statistics for Hour {selected_hour}',
    xaxis_title='Day of Week',
    yaxis_title='Duration (minutes)',
    xaxis=dict(
        tickmode='array',
        tickvals=list(range(7)),
        ticktext=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    ),
    template='plotly_dark'
)

# Display the plot in Streamlit
tab1.plotly_chart(fig)


tree_fare, tree_duration, linreg_tip_amount = load_model('outputs/models/tree_fare_amount.pkl'), \
                            load_model('outputs/models/tree_trip_duration.pkl'), \
                            load_model('outputs/models/tip_amount_model.pkl')


### The PREDICTION TAB 2
# Streamlit app
tab2.title('Trip Search')

# Text input for the address
input_origin_address = tab2.text_input('Origin:')
suggestions = []

orlat, orlng, destlat, destlng = None, None, None, None

if input_origin_address:
    suggestions = get_place_suggestions(input_origin_address)

if suggestions:
    selected_suggestion = tab2.selectbox('Suggestions:', [s['description'] for s in suggestions])
    selected_place_id = next(s['place_id'] for s in suggestions if s['description'] == selected_suggestion)
    orlat, orlng = get_place_details(selected_place_id)
    if orlat and orlng:
        tab2.write(f"You selected: {selected_suggestion}")
        tab2.write(f"Coordinates: Latitude {orlat}, Longitude {orlng}")
    else:
        tab2.write("Could not retrieve coordinates for the selected address.")

input_destination_address = tab2.text_input('Destination:')
suggestions = []

if input_destination_address:
    suggestions = get_place_suggestions(input_destination_address)

if suggestions:
    selected_suggestion = tab2.selectbox('Suggestions:', [s['description'] for s in suggestions])
    selected_place_id = next(s['place_id'] for s in suggestions if s['description'] == selected_suggestion)
    destlat, destlng = get_place_details(selected_place_id)
    if destlat and destlng:
        tab2.write(f"You selected: {selected_suggestion}")
        tab2.write(f"Coordinates: Latitude {destlat}, Longitude {destlng}")
    else:
        tab2.write("Could not retrieve coordinates for the selected address.")
else:
    tab2.write("Please start typing an address to see suggestions.")



# Layout for day of the week and time
col1, col2, col3, col4 = tab2.columns(4)

with col1:
    day_of_week = tab2.selectbox('Day:', 
                               ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    day_of_week_int = day_of_week_to_int(day_of_week)

with col2:
    hour = tab2.selectbox('Hour:', list(range(1, 13)))

with col3:
    minute = tab2.selectbox('Minute:', [f"{i:02}" for i in range(60)])

with col4:
    ampm = tab2.selectbox('AM/PM:', ['AM', 'PM'])

# Convert time to 24-hour format
if ampm == 'PM' and hour != 12:
    hour_24 = hour + 12
elif ampm == 'AM' and hour == 12:
    hour_24 = 0
else:
    hour_24 = hour


tab2.write(f"You selected: {day_of_week} at {hour:02}:{minute:02} {ampm}")
tab2.write(f"(day {day_of_week_int}, hour {hour_24}, minute {minute})")



if tab2.button('Submit'):
    # Call prediction functions here
    tab2.write(f"Origin Coordinates: Latitude {orlat}, Longitude {orlng}")
    tab2.write(f"Destination Coordinates: Latitude {destlat}, Longitude {destlng}")
    
    # Predict tip amount
    pred = make_prediction(hour_24,
                           minute,
                           day_of_week_int,
                           orlng,
                           orlat,
                           destlng,
                           destlat,
                           tree_targets=['fare_amount', 'trip_duration'],
                           tree_models=[tree_fare, tree_duration],
                           reg_targets=['tip_amount'],
                           reg_models=[linreg_tip_amount]
    ),
    
    tab2.write(f"Predicted trip duration: {pred['trip_duration']}")                       
    tab2.write(f"Predicted fare: {pred['fare_amount']}")
    tab2.write(f"Predicted tip amount: {pred['tip_amount']}")
    