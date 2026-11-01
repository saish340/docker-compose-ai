# CI/CD automatic deployment test
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from pymongo import MongoClient
from datetime import datetime
import os
import time

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb://mongodb:27017/"
)

client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
db = client["iris_database"]
collection = db["predictions"]

# Load dataset and train AI model
iris = load_iris()
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(iris.data, iris.target)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "AI Model API is running",
        "status": "success"
    })

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    features = data.get("features")

    if not isinstance(features, list) or len(features) != 4:
        return jsonify({"error": "Enter exactly 4 features"}), 400

    try:
        features = [float(x) for x in features]

        prediction = int(model.predict([features])[0])
        probabilities = model.predict_proba([features])[0]

        result = {
            "prediction": str(iris.target_names[prediction]),
            "class_id": prediction,
            "confidence": round(float(max(probabilities)), 4)
        }

        # Store prediction in MongoDB
        collection.insert_one({
            "features": features,
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "timestamp": datetime.utcnow()
        })

        return jsonify(result)

    except (ValueError, TypeError):
        return jsonify({"error": "Features must be numeric"}), 400
    except Exception as e:
        return jsonify({"error": "Prediction or database error"}), 500

@app.route("/history", methods=["GET"])
def history():
    records = list(
        collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(20)
    )

    for record in records:
        record["timestamp"] = record["timestamp"].isoformat()

    return jsonify(records)

if __name__ == "__main__":
    # Wait until MongoDB is available
    for attempt in range(15):
        try:
            client.admin.command("ping")
            print("Connected to MongoDB successfully")
            break
        except Exception:
            print("Waiting for MongoDB...")
            time.sleep(2)
    else:
        raise RuntimeError("Could not connect to MongoDB")

    app.run(host="0.0.0.0", port=5000)
