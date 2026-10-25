from flask import Flask, request, jsonify
import joblib
import pandas as pd
import io

# Initialize the Flask application
app = Flask(__name__)

# Load the serialized production-grade model pipeline
# The pipeline natively handles preprocessing, encoding, scaling, and prediction
model_path = "superkart_model.joblib"
try:
    model_pipeline = joblib.load(model_path)
    print("Success: Champion Pipeline loaded successfully!")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    model_pipeline = None

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "healthy",
        "message": "SuperKart Sales Forecasting API is up and running!"
    }), 200

@app.route('/v1/predict', methods=['POST'])
def predict():
    """Single instance online inference endpoint."""
    if not model_pipeline:
        return jsonify({"error": "Model is not loaded on server."}), 500

    try:
        # Retrieve payload from post request
        data = request.get_json(force=True)

        # Convert payload to Pandas DataFrame (single row prediction)
        input_df = pd.DataFrame([data])

        # Run prediction directly through the sklearn Pipeline
        prediction = model_pipeline.predict(input_df)[0]

        # Return rounded forecasted amount
        return jsonify({"prediction": float(round(prediction, 2))}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/v1/predictbatch', methods=['POST'])
def predict_batch():
    """Multi-instance batch inference CSV endpoint."""
    if not model_pipeline:
        return jsonify({"error": "Model is not loaded on server."}), 500

    try:
        # Check if CSV file is present in the request
        if 'file' not in request.files:
            return jsonify({"error": "No file key found in request files payload"}), 400

        file = request.files['file']
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "Uploaded file must be in CSV format"}), 400

        # Read raw CSV bytes stream into DataFrame
        stream = io.BytesIO(file.read())
        input_df = pd.read_csv(stream)

        # Run batch prediction through the pipeline
        predictions = model_pipeline.predict(input_df)

        # Package predicted sales paired with DataFrame index values
        predictions_dict = {str(i): float(round(pred, 2)) for i, pred in enumerate(predictions)}
        return jsonify(predictions_dict), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    # Run server locally on container port 7860
    app.run(host='0.0.0.0', port=7860, debug=True)
