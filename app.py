import subprocess
import os
import pandas as pd
from flask import Flask, render_template, jsonify

# Get base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/network")
def network():
    return render_template("network.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/scan", methods=["GET"])
def scan():
    try:
        print("🟢 Starting live packet capture...")

        # Run live_capture.py
        result1 = subprocess.run(["python", os.path.join(SRC_DIR, "live_capture.py")],
                                 capture_output=True, text=True, check=True)
        print("🔵 live_capture.py output:", result1.stdout)

        print("🔵 Running anomaly detection...")

        # Run predict.py
        result2 = subprocess.run(["python", os.path.join(SRC_DIR, "predict.py")],
                                 capture_output=True, text=True, check=True)
        print("🟠 predict.py output:", result2.stdout)

        # Read predictions
        predictions_file = os.path.join(BASE_DIR, "predictions.csv")
        if not os.path.exists(predictions_file):
            return jsonify({"status": "error", "message": "Predictions file not found!"}), 404

        df = pd.read_csv(predictions_file)
        anomaly_count = int(df["anomaly"].sum())

        # Dummy traffic data (replace with real if available)
        traffic_data = [
            {"time": "00:01", "count": 5},
            {"time": "00:02", "count": 2},
            {"time": "00:03", "count": 8},
            {"time": "00:04", "count": 3},
            {"time": "00:05", "count": 7}
        ]

        # Pie chart logic with safe fallback
        if anomaly_count == 0:
            anomaly_distribution = {
                "No Anomalies": 0 # Show green pie if no anomalies
            }
        else:
            ddos = max(1, int(anomaly_count * 0.6)) if anomaly_count < 3 else int(anomaly_count * 0.6)
            portscan = anomaly_count - ddos
            anomaly_distribution = {
                "DDoS": ddos,
                "Port Scan": portscan
            }

        return jsonify({
            "status": "success",
            "anomalies": anomaly_count,
            "traffic_data": traffic_data,
            "anomaly_distribution": anomaly_distribution
        })

    except subprocess.CalledProcessError as e:
        print(f"🔴 Error running script: {e.stderr}")
        return jsonify({"status": "error", "message": f"Script error: {e.stderr}"}), 500
    except Exception as e:
        print(f"🔴 Unexpected error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print("🟢 Flask app running at http://127.0.0.1:5000/")
    app.run(debug=True)


