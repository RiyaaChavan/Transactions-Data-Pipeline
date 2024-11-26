from flask import Flask, request, jsonify
from kafka import KafkaProducer
import pandas as pd
import json
from flask_cors import CORS
import time
time.sleep(10)
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
def json_serializer(data):
    return json.dumps(data).encode("utf-8")

producer = KafkaProducer(
    bootstrap_servers=["kafka:29092"], value_serializer=json_serializer
)

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Read CSV into a pandas DataFrame
        df = pd.read_csv(file)

        # Convert date column to datetime and then to string
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d %H:%M:%S")

        # Clean amount column by removing '$' and converting to float
        df["amount"] = df["amount"].str.replace("$", "").astype(float)

        # Send rows to Kafka
        for _, row in df.iterrows():
            data = {
                "id": int(row["id"]),
                "date": str(row["date"]),
                "client_id": str(row["client_id"]),
                "card_id": str(row["card_id"]),
                "amount": float(row["amount"]),
                "use_chip": bool(row["use_chip"]),
                "merchant_id": str(row["merchant_id"]),
                "merchant_city": str(row["merchant_city"]),
                "merchant_state": str(row["merchant_state"]),
                "zip": str(row["zip"]),
            }
            producer.send("financial_transactions", value=data)

        producer.flush()
        return jsonify({'message': 'File processed and data sent to Kafka'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)
