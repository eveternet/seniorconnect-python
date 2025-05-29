from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
from psycopg2 import pool
import psycopg
from api.database import get_db_connection
import os


load_dotenv()
connection_string = os.getenv("DATABASE_URL")

user_auth = Blueprint("user_auth", __name__)


@user_auth.route("/", methods=["POST"])
@user_auth.route("", methods=["POST"])
def authUser():
    print("debugging line 1: function called")
    print("Headers:", dict(request.headers))
    print("Data:", request.data)
    print("Is JSON:", request.is_json)
    try:
        data = request.get_json(force=False, silent=False)
    except Exception as e:
        print("Error parsing JSON:", e)
        return jsonify({"error": "Invalid JSON", "details": str(e)}), 400

    if not data:
        print("No data provided or JSON parse failed")
        return jsonify({"error": "No data provided"}), 400

    phone = data.get("phone")
    name = data.get("name")
    clerk_user_id = data.get("clerk_user_id")

    if not phone or not name or not clerk_user_id:
        return jsonify({"error": "Missing required fields"}), 400
    if (
        not isinstance(phone, str)
        or not isinstance(name, str)
        or not isinstance(clerk_user_id, str)
    ):
        return jsonify({"error": "Invalid data type"}), 400

    print("debugging line 2: got request")
    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        check_sql = "SELECT * FROM users WHERE clerk_user_id = %s"
        cur.execute(check_sql, (clerk_user_id,))
        existing_user_row = cur.fetchone()
        print("debugging line 3: got row")
        if existing_user_row:
            return jsonify({"message": "User already exists"}), 200
        else:
            insert_sql = """
            INSERT INTO users (clerk_user_id, display_name, phone_number)
            VALUES (%s, %s, %s)
            RETURNING id;
            """
            cur.execute(insert_sql, (clerk_user_id, name, phone))
            new_id = cur.fetchone()[0]
            conn.commit()
            return (
                jsonify(
                    {
                        "message": "User successfully onboarded",
                        "user_id": new_id,
                        "clerk_user_id": clerk_user_id,
                    }
                ),
                201,
            )
    except psycopg.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error during onboarding: {e}")
        return jsonify({"message": "An internal server error occurred"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
