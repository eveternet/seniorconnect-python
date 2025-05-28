from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import psycopg

# Importing blueprints
from api.user import user_blueprints

# dot env
load_dotenv()


# Initialise App
app = Flask(__name__)

# CORS shenanagans
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
CORS(app, origins=allowed_origins)

# Registering blueprints
app.register_blueprint(user_blueprints, url_prefix="/api/user")


# "Main" response
@app.route("/")
def home():
    return jsonify({"yes": "dis a response"})


# Uncomment this if you are deploying locally for testing
"""
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
"""
