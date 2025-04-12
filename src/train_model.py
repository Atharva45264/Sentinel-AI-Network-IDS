import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau   
from sklearn.metrics import classification_report, confusion_matrix

# 1. Load dataset
data = pd.read_csv("datasets\\preprocessed_data.csv")

# 2. Drop label columns and separate features (X) and target (y)
X = data.drop(columns=["Label_0", "Label_1", "Label_2", "Label_3", "Label_4", "Label_5", "Label_6", 
                       "Label_7", "Label_8", "Label_9", "Label_10", "Label_11", "Label_12", "Label_13", 
                       "Label_14", "Label_15", "Label_16", "Label_17", "Label_18", "Label_19", "Label_20", 
                       "Label_21", "Label_22", "Label_23", "Label_24", "Label_25", "Label_26"])  # Features
y = data["Label_0"]  # Target (example using 'Label_0')

# 3. Label encoding for target variable
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

# 4. Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Feature Scaling (StandardScaler)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test) 

# Convert to correct data types
X_train = X_train.astype(np.float32)
X_test = X_test.astype(np.float32)
y_train = y_train.astype(np.int32)
y_test = y_test.astype(np.int32)

# 6. Define Model
model = Sequential([
    Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    BatchNormalization(),
    Dropout(0.3),

    Dense(64, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),

    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')  # Use 'softmax' for multi-class classification
])

# 7. Compile Model with Optimizer and Loss
model.compile(optimizer=Adam(learning_rate=0.0005), 
              loss='binary_crossentropy', 
              metrics=['accuracy'])

# 8. Add Callbacks (EarlyStopping and ReduceLROnPlateau)
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1)

# 9. Train Model with More Epochs & Callbacks
history = model.fit(X_train, y_train,
                    epochs=20, batch_size=128,
                    validation_data=(X_test, y_test),
                    callbacks=[early_stopping, reduce_lr])

# 10. Evaluate Model
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Loss: {loss}")
print(f"Test Accuracy: {accuracy}")

# 11. Save Model in New Format
model.save('network_anomaly_model.keras')
print("Model saved as 'network_anomaly_model.keras'")

# 12. Load the Model and Re-evaluate
loaded_model = keras.models.load_model('network_anomaly_model.keras')
loss, accuracy = loaded_model.evaluate(X_test, y_test)
print(f"Loaded Model - Test Loss: {loss}")
print(f"Loaded Model - Test Accuracy: {accuracy}")

# 13. Additional Evaluation Metrics
y_pred = loaded_model.predict(X_test)
y_pred_classes = (y_pred > 0.5).astype("int32")

print(classification_report(y_test, y_pred_classes))
print(confusion_matrix(y_test, y_pred_classes))
