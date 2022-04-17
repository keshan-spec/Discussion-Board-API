import os
from flask import jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# custom imports
from app import create_app

# create and configure the flask app
env_name = os.getenv("FLASK_ENV")
API_PORT = os.getenv("API_PORT")
API_URL = "/api/v1"

# create app and configure CORS
app = create_app(env_name)
cors = CORS(app, supports_credentials=True)
app.config["CORS_HEADERS"] = "Content-Type"

# create the api blueprint
from routes.auth import auth_bp
from routes.user import user_bp

app.register_blueprint(auth_bp, url_prefix=API_URL)
app.register_blueprint(user_bp, url_prefix=API_URL)


# ROUTES: Error Handles
@app.errorhandler(404)
def not_found(error):
    return jsonify({"ERROR": "Invalid route!"}), 404


@app.errorhandler(500)
def internal_server(error):
    return jsonify({"ERROR": "Internal server error!"}), 500

# ROUTE: Index
@app.route("/")
def home():
    return jsonify(f"API URL -> {API_URL}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=API_PORT)  # run app
