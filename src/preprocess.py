import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam

def preprocess_live_data(live_data_path):
    # Load live data
    data_live = pd.read_csv(live_data_path)

    # Print columns to verify and debug
    print("Columns in live data:", data_live.columns.tolist())  # Show all column names

    # Define selected columns (the ones you expect in live data)
    selected_columns = ['Flow Duration', 'Total Fwd Packet', 'Total Bwd packets', 
                        'Total Length of Fwd Packet', 'Total Length of Bwd Packet', 
                        'Fwd Packet Length Max', 'Bwd Packet Length Max', 'Protocol', 'Timestamp']
    
    # Check which selected columns are missing in live data
    missing_columns = [col for col in selected_columns if col not in data_live.columns]
    if missing_columns:
        print(f"Missing columns in live data: {missing_columns}")
        # Handle missing columns by adding them with default values (e.g., zero)
        for col in missing_columns:
            data_live[col] = 0  # Adding the missing columns with default value (0 or appropriate value)
        print("Added missing columns with default values.")
    
    # Now select the columns you need
    try:
        data_live = data_live[selected_columns]
    except KeyError as e:
        print(f"Error selecting columns: {e}")
        raise

    # Convert 'Timestamp' to seconds (same format as training data)
    if 'Timestamp' in data_live.columns:
        try:
            data_live['Timestamp'] = pd.to_datetime(data_live['Timestamp'], format="%d/%m/%Y %H:%M", errors='coerce')
        except Exception as e:
            print(f"Error converting Timestamp: {e}")
            data_live['Timestamp'] = pd.to_datetime(data_live['Timestamp'], errors='coerce')
        data_live['Timestamp'] = data_live['Timestamp'].astype('int64') // 10**9  # Convert to seconds

    # One-hot encode 'Protocol' column
    if 'Protocol' in data_live.columns:
        data_live = pd.get_dummies(data_live, columns=['Protocol'])
    
    # Handle missing values by forward filling
    data_live = data_live.ffill()

    # Return the preprocessed data
    return data_live
