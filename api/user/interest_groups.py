from flask import Blueprint, abort, jsonify, request
from dotenv import load_dotenv
from psycopg2 import pool
import psycopg
from api.database import get_db_connection
import os

load_dotenv()
connection_string = os.getenv("DATABASE_URL")

interest_groups = Blueprint("interest_groups", __name__)


@interest_groups.route("/info", methods=["GET"])
def get_info():
    return jsonify(
        [
            {
                "name": "Chess",
                "description": "Play a fun game that keeps your brain sharp. Learn new moves!",
            },
            {
                "name": "Checkers",
                "description": "A classic game! Easy to learn, fun to play. Use your thinking.",
            },
            {
                "name": "Mahjong",
                "description": "Play with tiles! A classic game from far away. Good for your mind and friends.",
            },
            {
                "name": "Poker",
                "description": "Play cards together! A fun game. Use your quick thinking. Just for fun!",
            },
            {
                "name": "Yoga",
                "description": "Gentle moves to feel good. Helps you bend and feel calm.",
            },
            {
                "name": "Photography",
                "description": "Take pictures! Use your camera or phone. Show what you see.",
            },
        ]
    )
