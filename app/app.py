import streamlit as st
import requests

# Fetch API key from Streamlit Secrets
API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]

# Get place predictions
def get_place_suggestions(input_text):
    url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input={input_text}&types=geocode&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        predictions = response.json().get('predictions', [])
        return [item['description'] for item in predictions]
    else:
        return []

#st.title('Address')

# Text input for the address
input_address = st.text_input('Enter an address:')
suggestions = []

if input_address:
    suggestions = get_place_suggestions(input_address)

if suggestions:
    selected_suggestion = st.selectbox('Suggestions:', suggestions)
    st.write(f"You selected: {selected_suggestion}")
else:
    st.write("Please start typing an address to see suggestions.")
