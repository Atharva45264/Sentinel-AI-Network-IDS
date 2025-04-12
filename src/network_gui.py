import sys
import subprocess
import pandas as pd
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout

class NetworkScannerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set window properties
        self.setWindowTitle('Network Anomaly Detector')
        self.setGeometry(200, 200, 400, 200)

        # Button to start scan
        self.scan_button = QPushButton('Scan', self)
        self.scan_button.clicked.connect(self.start_scan)

        # Label to show anomaly count
        self.result_label = QLabel('Anomalies Detected: 0', self)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.scan_button)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

    def start_scan(self):
        """Captures packets and predicts anomalies"""
        self.result_label.setText("Scanning... Please wait")

        try:
            # Run live packet capture
            subprocess.run(["python", "src/live_capture.py"], check=True)

            # Wait to ensure live_capture has finished
            time.sleep(5)  # Adjust delay if needed

            # Run anomaly detection
            subprocess.run(["python", "src/predict.py"], check=True)

            # Wait a moment for predictions to be saved
            time.sleep(2)

            # Read the results
            df = pd.read_csv("predictions.csv")
            anomaly_count = df["anomaly"].sum()
            self.result_label.setText(f"Anomalies Detected: {anomaly_count}")

        except subprocess.CalledProcessError as e:
            self.result_label.setText(f"Error running script: {e}")
        except Exception as e:
            self.result_label.setText(f"Error reading results: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NetworkScannerApp()
    ex.show()
    sys.exit(app.exec_())

