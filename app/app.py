import streamlit as st
import requests
from utils import get_place_suggestions, get_place_details, day_of_week_to_int

tab1, tab2 = st.tabs(["📈 Exploration", "🗃 Prediction"])

# Fetch API key from Streamlit Secrets
API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]

# Streamlit app
tab2.title('Trip Search')

# Text input for the address
input_origin_address = tab2.text_input('Origin:')
suggestions = []

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
#write origin and destination coordinates
#tab2.write(f"Origin Coordinates: Latitude {orlat}, Longitude {orlng}")
#tab2.write(f"Destination Coordinates: Latitude {destlat}, Longitude {destlng}")