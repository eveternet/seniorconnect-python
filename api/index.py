from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
load_dotenv()

# Importing blueprints
from user.interest_groups import interest_groups

# Initialise App
app = Flask(__name__)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

# Registering blueprints
app.register_blueprint(interest_groups, url_prefix='/api/interest_groups')


@app.route('/')
def home():
    return jsonify({"yes": "dis a response"})

"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
"""