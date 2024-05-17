import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from geopy.distance import geodesic
import pickle
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

import pandas as pd

def load_data(file_path: str, sample_size: float) -> pd.DataFrame:
    """
    Load data from a CSV file and return a sample of the specified size.

    Args:
        file_path (str): The path to the CSV file.
        sample_size (float): The proportion of the data to sample. Should be a value between 0 and 1.

    Returns:
        pd.DataFrame: A DataFrame containing the sampled data.
    """
    df = pd.read_csv(file_path)
    df = df.sample(int(len(df) * sample_size))
    logger.info(f'Finished loading data. Shape: {df.shape}')
    return df

def drop_nulls_and_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Drop specified columns and remove rows with null values from a DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.
        columns (list): A list of column names to be dropped.

    Returns:
        pd.DataFrame: The modified DataFrame with dropped columns and removed rows with null values.
    """
    df = df.drop(columns, axis=1)
    df = df.dropna()
    logger.info("Dropped columns")
    return df

def remove_outliers(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Remove outliers from the given DataFrame based on the specified columns.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        columns (list): A list of column names to consider for outlier removal.

    Returns:
        pd.DataFrame: The DataFrame with outliers removed.
    """
    impossible_dates = df.query('pickup_datetime > dropoff_datetime').index
    df = df.drop(impossible_dates, axis=0)

    for column in columns:
        Q1 = df[column].quantile(0.08)
        Q3 = df[column].quantile(0.92)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    
    df = df[df['trip_distance'] > 0]
    df = df[df['fare_amount'] < 100]
    df = df[df['trip_distance'] < 60]
    df = df[df['tip_amount'] / df['fare_amount']<.4]
    
    trip_quant = df['trip_duration'].quantile(.995)
    dropoff_max = df['dropoff_longitude'].quantile(0.98)
    dropoff_min = df['dropoff_longitude'].quantile(0.02)
    
    df = df.query("dropoff_longitude < @dropoff_max and dropoff_longitude > @dropoff_min")
    df = df.query("trip_duration < @trip_quant")
    df = df.query("rate_code == 1 or rate_code == 2 or rate_code == 3 or rate_code == 4")
    logger.info("Removed outliers")
    return df

def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create time-related features from the given DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing pickup and dropoff datetime columns.

    Returns:
        pd.DataFrame: The DataFrame with additional time-related features.

    """
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
    df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])

    df['start_hour'] = df['pickup_datetime'].dt.hour
    df['start_minute'] = df['pickup_datetime'].dt.minute
    df['trip_duration'] = (df['dropoff_datetime'] - df['pickup_datetime']).dt.total_seconds() / 60
    df['day_of_week'] = df['pickup_datetime'].dt.dayofweek
    logger.info("Created time features")
    return df

def create_geo_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create geo features based on pickup and dropoff coordinates.

    Args:
        df (pd.DataFrame): The input DataFrame containing pickup and dropoff coordinates.

    Returns:
        pd.DataFrame: The DataFrame with additional geo features.

    """
    df['gps_distance'] = df.apply(lambda x: geodesic((x['pickup_latitude'], x['pickup_longitude']), (x['dropoff_latitude'], x['dropoff_longitude'])).miles, axis=1)
    logger.info("Created geo features")
    return df

def split_data(df: pd.DataFrame, features: list, target: str, train_size:float = 0.6, val_test_split:float = 0.5, random_state=42, shuffle=True) -> tuple:
    """
    Split the data into training, validation, and test sets.

    Parameters:
    - df (pd.DataFrame): The input DataFrame containing the data.
    - features (list): The list of feature column names.
    - target (str): The name of the target column.
    - train_size (float): The proportion of the data to use for training (default: 0.6).
    - val_test_split (float): The proportion of the remaining data to split between validation and test sets (default: 0.5).
    - random_state (int): The random seed for reproducibility (default: 42).
    - shuffle (bool): Whether to shuffle the data before splitting (default: True).

    Returns:
    - tuple: A tuple containing the following elements:
        - X_train (pd.DataFrame): The training set features.
        - X_val (pd.DataFrame): The validation set features.
        - X_test (pd.DataFrame): The test set features.
        - y_train (pd.Series): The training set target.
        - y_val (pd.Series): The validation set target.
        - y_test (pd.Series): The test set target.
    """
    X = df[features]
    y = df[target]
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, train_size=train_size, random_state=random_state, shuffle=shuffle)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=val_test_split, random_state=random_state, shuffle=shuffle)
    logger.info("Split data")
    return X_train, X_val, X_test, y_train, y_val, y_test

def train_tree(X_train: pd.DataFrame, y_train: pd.Series, X_val: pd.DataFrame, y_val: pd.Series, max_depth: int) -> DecisionTreeRegressor:
    """
    Trains a decision tree regressor model using the provided training data and returns the trained model.

    Parameters:
    - X_train (pd.DataFrame): The input features for training.
    - y_train (pd.Series): The target variable for training.
    - X_val (pd.DataFrame): The input features for validation.
    - y_val (pd.Series): The target variable for validation.
    - max_depth (int): The maximum depth of the decision tree.

    Returns:
    - tree (DecisionTreeRegressor): The trained decision tree regressor model.
    """
    tree = DecisionTreeRegressor(max_depth=max_depth)
    tree.fit(X_train, y_train)
    score = tree.score(X_val, y_val)
    logger.info(f"Trained Tree Regressor with r² score of {score:.2f}")
    return tree

def pickle_model(tree: DecisionTreeRegressor, file_path: str) -> None:
    """
    Pickles a DecisionTreeRegressor object and saves it to a file.

    Parameters:
    tree (DecisionTreeRegressor): The DecisionTreeRegressor object to be pickled.
    file_path (str): The file path where the pickled object will be saved.

    Returns:
    None
    """
    with open(file_path, 'wb') as file:
        pickle.dump(tree, file)
    logger.info(f"Tree saved to {file_path}")

def load_model(file_path: str) -> DecisionTreeRegressor:
    """
    Load a decision tree from a file.

    Parameters:
        file_path (str): The path to the file containing the decision tree.

    Returns:
        DecisionTreeRegressor: The loaded decision tree.

    """
    with open(file_path, 'rb') as file:
        tree = pickle.load(file)
    return tree

def make_prediction(hour: int,
                    minute: int,
                    day_of_week: int,
                    pickup_lat: float,
                    pickup_long: float,
                    dropoff_lat: float,
                    dropoff_long: float,
                    tree_targets: list,
                    tree_models: list,
                    reg_targets: list,
                    reg_models: list):
    """
    Make a prediction using the given input parameters and return the predictions for each target.

    Parameters:
    hour (int): The hour of the pickup time.
    minute (int): The minute of the pickup time.
    day_of_week (int): The day of the week (0-6, where Monday is 0 and Sunday is 6).
    pickup_lat (float): The latitude of the pickup location.
    pickup_long (float): The longitude of the pickup location.
    dropoff_lat (float): The latitude of the dropoff location.
    dropoff_long (float): The longitude of the dropoff location.
    targets (list): A list of target names.
    models (list): A list of machine learning models.

    Returns:
    dict: A dictionary containing the predictions for each target, where the target name is the key and the prediction is the value.
    """
    
    output = {}

    gps_distance = geodesic((pickup_lat, pickup_long), (dropoff_lat, dropoff_long)).miles
    passenger_count = 1
    rate_code = 1

    tree_input = np.array(
        [
            hour,
            minute,
            passenger_count,
            pickup_long,
            pickup_lat,
            dropoff_long,
            dropoff_lat,
            rate_code,
            day_of_week,
            gps_distance
        ]
    ).reshape(1, -1)

    regression_input = np.array(
        [
            hour,
            day_of_week,
            gps_distance,
            pickup_lat,
            pickup_long,
        ]
    ).reshape(1, -1)

    for model, target in zip(tree_models, tree_targets):    
        predictions = model.predict(tree_input)
        output[target] = predictions[0] 

    for model, target in zip(reg_models, reg_targets):
        predictions = model.predict(regression_input)
        output[target] = predictions[0]
    
    return output