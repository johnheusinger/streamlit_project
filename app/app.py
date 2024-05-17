import streamlit as st
import requests

# Fetch API key from Streamlit Secrets
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

# Streamlit app
st.title('Trip Search')

# Text input for the address
input_origin_address = st.text_input('Origin:')
suggestions = []

if input_origin_address:
    suggestions = get_place_suggestions(input_origin_address)

if suggestions:
    selected_suggestion = st.selectbox('Suggestions:', [s['description'] for s in suggestions])
    selected_place_id = next(s['place_id'] for s in suggestions if s['description'] == selected_suggestion)
    lat, lng = get_place_details(selected_place_id)
    if lat and lng:
        st.write(f"You selected: {selected_suggestion}")
        st.write(f"Coordinates: Latitude {lat}, Longitude {lng}")
    else:
        st.write("Could not retrieve coordinates for the selected address.")
#else:
#    st.write("Please start typing an address to see suggestions.")

input_destination_address = st.text_input('Destination:')
suggestions = []

if input_destination_address:
    suggestions = get_place_suggestions(input_destination_address)

if suggestions:
    selected_suggestion = st.selectbox('Suggestions:', [s['description'] for s in suggestions])
    selected_place_id = next(s['place_id'] for s in suggestions if s['description'] == selected_suggestion)
    lat, lng = get_place_details(selected_place_id)
    if lat and lng:
        st.write(f"You selected: {selected_suggestion}")
        st.write(f"Coordinates: Latitude {lat}, Longitude {lng}")
    else:
        st.write("Could not retrieve coordinates for the selected address.")
else:
    st.write("Please start typing an address to see suggestions.")
