import pandas as pd
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler

# Define all 12 features the model expects
expected_features = [
    'protocol', 'src_port', 'dst_port', 'length', 'flow duration',
    'total fwd packet', 'total bwd packets', 'total length of fwd packet',
    'total length of bwd packet', 'fwd packet length max', 'bwd packet length max',
    'packet length mean'
]

def preprocess_live_data(live_data_path):
    """Loads, cleans, and preprocesses live packet data for prediction."""
    try:
        # Load live data
        df = pd.read_csv(live_data_path)

        # Convert column names to lowercase
        df.columns = df.columns.str.strip().str.lower()

        # Live data available features
        available_features = ['protocol', 'src_port', 'dst_port', 'length']

        # Initialize missing features with 0
        for feature in expected_features:
            if feature not in df.columns:
                df[feature] = 0  # Fill missing features with 0

        # Select only the expected features
        df = df[expected_features]

        # Convert protocol to numeric (if necessary, convert to one-hot encoding)
        df['protocol'] = pd.to_numeric(df['protocol'], errors='coerce')

        # Fill NaN values with 0
        df.fillna(0, inplace=True)

        # Normalize data
        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(df)

        return df_scaled

    except Exception as e:
        print(f"❌ Error in preprocessing: {e}")
        return None

def predict_anomalies(csv_file="live_packets.csv"):
    """Loads model and predicts anomalies in network traffic."""
    try:
        # Preprocess the live data
        live_data = preprocess_live_data(csv_file)

        if live_data is None:
            print("❌ Prediction aborted due to preprocessing error.")
            return  

        # Debugging: Print the shape of preprocessed data
        print(f"✅ Shape of preprocessed live data: {live_data.shape}")  # Should be (N, 12)

        # Load trained model
        model = keras.models.load_model('network_anomaly_model.keras')

        # Predict anomalies
        predictions = model.predict(live_data)

        # Convert predictions to binary anomaly labels
        anomalies = (predictions > 0.5).astype(int)

        # Save predictions to CSV
        pd.DataFrame(anomalies, columns=["anomaly"]).to_csv("predictions.csv", index=False)
        print("✅ Predictions saved to predictions.csv")

    except Exception as e:
        print(f"❌ Error in prediction: {e}")

# Run prediction
predict_anomalies("live_packets.csv")
