import streamlit as st
import pandas as pd
import numpy as np

tab1, tab2 = st.tabs(["📈 Exploration", "🗃 Prediction"])

import joblib
import pandas as pd


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
    model = joblib.load('tip_amount_model.pkl')
    

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


# The stuff under tab1.xyz are all exploration related UI eliments.
tab1.subheader("A tab with a chart")
df = pd.read_csv("data/outputs/VisualizeLocations.csv")
# pickups = pd.read_csv("data/processed_data/PickupLocations.csv")
# dropoff = pd.read_csv("data/processed_data/DropoffLocations.csv")

df20 =  df.head(20000)
# pick_df20 =  pickups.head(20000)
# drop_df20 =  dropoff.head(20000)

tab1.map(df20, size=2, color='color')


# The stuff under tab2.xyz are all prediction related UI eliments and the predictions.
tab2.subheader("A tab with the data")
tab2.write(df20)


# # Sample df DataFrame
# sampled_df = df.sample(frac=0.0005, random_state=1)