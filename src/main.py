from functions import *

if __name__ == '__main__':
    DATA_PATH: str = '../data/ny_cab_csv/nyc_taxi_data_2014.csv'
    OUT_PATH: str = '../models/'
    SAMPLE:float = 3e-2
    DROP_COLUMNS: list = ['store_and_fwd_flag']
    OUTLIER_COLUMNS: list = ['pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude']
    FEATURES: list = [
        'start_hour',
        'start_minute',
        'passenger_count',
        'pickup_longitude',
        'pickup_latitude',
        'dropoff_longitude',
        'dropoff_latitude',
        'rate_code',
        'day_of_week',
        'gps_distance'
        ]
    TARGETS: list = [
        'fare_amount',
        'trip_duration'
        ]
    TRAIN_SIZE: float = 6e-1
    VAL_TEST_SPLIT: float = 5e-1
    MAX_DEPTH = 10
    
    df = load_data(DATA_PATH, SAMPLE)
    df = drop_nulls_and_columns(df, DROP_COLUMNS)
    df = create_time_features(df)
    df = remove_outliers(df, OUTLIER_COLUMNS)
    df = create_geo_features(df)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(df, FEATURES, TARGETS, TRAIN_SIZE, VAL_TEST_SPLIT, random_state=42, shuffle=True)
    
    for target in TARGETS:
        tree = train_tree(X_train, y_train[target], X_val, y_val[target], MAX_DEPTH)
        file_name = 'tree_' + str(target) + '.pkl'
        file_path = OUT_PATH + file_name
        pickle_tree(tree, file_path)