from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
from psycopg2 import pool
import psycopg
from ..index import get_db_connection
import os


load_dotenv()
connection_string = os.getenv("DATABASE_URL")

user_auth = Blueprint("user_auth", __name__, url_prefix="/auth")


@user_auth.route("/", methods=["POST"])
def authUser():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    phone = data.get("phone")
    name = data.get("name")
    userid = data.get("clerk_user_id")
    if not phone or not name or not userid:
        return jsonify({"error": "Missing required fields"}), 400
    if phone.type != "string" or name.type != "string" or userid.type != "string":
        return jsonify({"error": "Invalid data type"}), 400

    # Checking database if user exists
    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        check_sql = "SELECT * FROM users WHERE clerk_user_id = %s"
        cur.execute(check_sql, (clerk_user_id))
        existing_user_row = cur.fetchone()
        if existing_user_row:
            return jsonify({"Success": "User already exists"}), 204
        else:
            insert_sql = """
            INSERT INTO users (clerk_user_id, name, phone)
            VALUES (%s, %s, %s)
            RETURNING id;
            """
            cur.execute(insert_sql, (clerk_user_id, name, phone, email))
            new_id = cur.fetchone()[0]

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
            cur.close()  # Close cursor first
        if conn:
            conn.close()  # Then close connection
