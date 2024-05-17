# NYC Taxi Data Exploration and ML Model Deployment with Streamlit

## Introduction:
The NYC Taxi Data project aims to explore and analyze the New York City taxi dataset obtained from Kaggle's competition. This dataset contains detailed information about taxi rides in NYC, including pickup and dropoff locations, timestamps, trip durations, fares, and more. The project utilizes Streamlit, a powerful Python library for building interactive web applications, to demonstrate interactive data exploration and the deployment of machine learning models.

## About the Dataset:
The NYC Taxi dataset provides a rich source of information for understanding travel patterns, traffic congestion, and taxi service dynamics in New York City. It includes millions of taxi trips recorded over several years, offering insights into passenger behavior, trip duration, fare variability, and spatial distribution across the city.

## Visualization 1: Sample NYC Taxi Data
The first visualization showcases a sample of the NYC taxi dataset. We filtered the data to remove outliers and anomalies, ensuring a more accurate representation of typical taxi rides in the city. This visualization provides an overview of key variables such as trip duration, fare amount, pickup/dropoff locations, and passenger count.

## Visualization 2: Travel Time to JFK Airport
The second visualization focuses on travel time to John F. Kennedy International Airport (JFK) from various locations across NYC. By analyzing historical taxi trip data, we calculate the average travel time from different pickup locations to JFK airport. This visualization helps commuters and travelers estimate their travel time to the airport based on their starting point within the city.

## Prediction Tab:
The Prediction tab in the Streamlit app allows users to interactively predict taxi fare, trip duration, and recommended tip for a given address in NYC. Users can input their pickup address, which is validated and geocoded using the Google Maps API to extract GPS coordinates. The machine learning model then predicts the fare amount, trip duration, and suggested tip for the specified ride, providing users with valuable insights before booking their taxi.

## Conclusion:
The NYC Taxi Data project offers a comprehensive exploration of taxi ride patterns in New York City, coupled with interactive visualizations and predictive modeling capabilities using Streamlit. Whether for analyzing travel trends, estimating trip costs, or planning airport transfers, this project provides valuable tools for both commuters and taxi service providers in NYC.
