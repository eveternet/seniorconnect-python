from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import psycopg

# Importing blueprints
from api.user import user_blueprints

# dot env
load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable not set. Please create a .env file."
    )


def get_db_connection():
    try:
        conn = psycopg.connect(DATABASE_URL)
        return conn
    except psycopg.Error as e:
        print(f"Error connecting to database: {e}")
        # In a real app, you might log this error more formally
        raise


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
