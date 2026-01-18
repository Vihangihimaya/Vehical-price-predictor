from flask import Flask, render_template, request, jsonify, send_from_directory
from price_service import predict_price_ml, predict_price_gpt
import os

# === Define base paths ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../Frontend"))
STATIC_DIR = os.path.join(FRONTEND_DIR, "images")  # Static assets

# === Initialize Flask ===
app = Flask(
    __name__,
    template_folder=FRONTEND_DIR,
    static_folder=STATIC_DIR
)

# === Home page ===
@app.route("/")
def home():
    return render_template("index.html")

# === Dynamic routing for pages like predict.html, about.html ===
@app.route("/<page_name>")
def serve_page(page_name):
    try:
        return render_template(page_name)
    except:
        return "Page not found", 404

# === Unified API: ML & GPT prediction ===
@app.route("/predict", methods=["POST"])
def predict_api():
    try:
        data = request.get_json()
        brand = data.get("brand")
        model = data.get("model")
        year = data.get("year")
        location = data.get("area", "Colombo")
        mode = data.get("mode")

        # Include condition fields for ML
        conditions = {
            "paint_condition": data.get("paint_condition"),
            "engine_condition": data.get("engine_condition"),
            "tire_condition": data.get("tire_condition"),
            "scratches_dents": data.get("scratches_dents"),
            "facelift": data.get("facelift"),
            "mileage": data.get("mileage"),
            "fuel_efficiency": data.get("fuel_efficiency"),
            "service_records": data.get("service_records"),
            "interior_condition": data.get("interior_condition"),
        }

        if mode == "ml":
            price = predict_price_ml(brand, model, year, location, conditions)
            return jsonify({"mode": "ml", "price": price})

        elif mode == "gpt":
            result = predict_price_gpt(brand, model, year)
            return jsonify({"mode": "gpt", "result": result})

        else:
            return jsonify({"error": "Invalid prediction mode."}), 400

    except Exception as e:
        print("Prediction API error:", str(e))
        return jsonify({"error": "Server error during prediction."}), 500

# === Serve static files like images ===
@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(STATIC_DIR, filename)

# === Run Flask app ===
if __name__ == "__main__":
    app.run(debug=True, port=5050)