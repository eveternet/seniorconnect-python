from flask import Blueprint, abort, jsonify, request
from dotenv import load_dotenv
from psycopg2 import pool
import psycopg
from api.database import get_db_connection
import os

load_dotenv()
connection_string = os.getenv("DATABASE_URL")

interest_groups = Blueprint("interest_groups", __name__)


@interest_groups.route("/info/all", methods=["GET"])
def all_groups():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT ig.id, ig.name, ig.description, u.display_name AS creator_name
            FROM interest_groups ig
            JOIN users u ON ig.creator_id = u.id
            ORDER BY ig.name
        """
        )
        rows = cur.fetchall()
        groups = [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "creator_name": row[3],
            }
            for row in rows
        ]
        return jsonify({"groups": groups}), 200
    except psycopg.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "An internal server error occurred"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@interest_groups.route("/info/<group_id>", methods=["GET"])
def group_info(group_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT ig.id, ig.name, ig.description, u.display_name AS creator_name
            FROM interest_groups ig
            JOIN users u ON ig.creator_id = u.id
            WHERE ig.id = %s
        """,
            (group_id,),
        )
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Group does not exist"}), 404
        group_info = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "creator_name": row[3],
        }
        return jsonify(group_info), 200
    except psycopg.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "An internal server error occurred"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@interest_groups.route("/join/<group_id>", methods=["POST"])
def join(group_id):
    try:
        data = request.get_json(force=False, silent=False)
    except Exception as e:
        return jsonify({"error": "Invalid JSON", "details": str(e)}), 400

    if not data:
        return jsonify({"error": "No data provided"}), 400

    clerk_user_id = data.get("clerk_user_id")
    if not clerk_user_id or not isinstance(clerk_user_id, str):
        return jsonify({"error": "No user id provided / Invalid user id type"}), 400

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 1. Check user exists and get user UUID
        cur.execute("SELECT id FROM users WHERE clerk_user_id = %s", (clerk_user_id,))
        user_row = cur.fetchone()
        if not user_row:
            return jsonify({"error": "User does not exist"}), 404
        user_uuid = user_row[0]

        # 2. Check group exists
        cur.execute("SELECT id FROM interest_groups WHERE id = %s", (group_id,))
        group_row = cur.fetchone()
        if not group_row:
            return jsonify({"error": "Group does not exist"}), 404
        group_uuid = group_row[0]

        # 3. Check if already a member
        cur.execute(
            "SELECT id FROM group_memberships WHERE user_id = %s AND group_id = %s",
            (user_uuid, group_uuid),
        )
        if cur.fetchone():
            return jsonify({"error": "User already a member of this group"}), 409

        # 4. Insert membership
        cur.execute(
            "INSERT INTO group_memberships (user_id, group_id) VALUES (%s, %s)",
            (user_uuid, group_uuid),
        )
        conn.commit()
        return jsonify({"message": "User successfully joined the group"}), 201

    except psycopg.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "An internal server error occurred"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@interest_groups.route("/leave/<group_id>", methods=["POST"])
def leave(group_id):
    try:
        data = request.get_json(force=False, silent=False)
    except Exception as e:
        return jsonify({"error": "Invalid JSON", "details": str(e)}), 400

    if not data:
        return jsonify({"error": "No data provided"}), 400

    clerk_user_id = data.get("clerk_user_id")
    if not clerk_user_id or not isinstance(clerk_user_id, str):
        return jsonify({"error": "No user id provided / Invalid user id type"}), 400

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 1. Check user exists and get user UUID
        cur.execute("SELECT id FROM users WHERE clerk_user_id = %s", (clerk_user_id,))
        user_row = cur.fetchone()
        if not user_row:
            return jsonify({"error": "User does not exist"}), 404
        user_uuid = user_row[0]

        # 2. Check group exists and get creator_id
        cur.execute(
            "SELECT id, creator_id FROM interest_groups WHERE id = %s", (group_id,)
        )
        group_row = cur.fetchone()
        if not group_row:
            return jsonify({"error": "Group does not exist"}), 404
        group_uuid, creator_uuid = group_row

        # 3. Prevent creator from leaving
        if user_uuid == creator_uuid:
            return (
                jsonify(
                    {
                        "error": "Creators must transfer ownership before leaving the group."
                    }
                ),
                403,
            )

        # 4. Check if already a member
        cur.execute(
            "SELECT id FROM group_memberships WHERE user_id = %s AND group_id = %s",
            (user_uuid, group_uuid),
        )
        if not cur.fetchone():
            return jsonify({"error": "User is not a member of this group"}), 409

        # 5. Delete membership
        cur.execute(
            "DELETE FROM group_memberships WHERE user_id = %s AND group_id = %s",
            (user_uuid, group_uuid),
        )
        conn.commit()
        return jsonify({"message": "User successfully left the group"}), 200

    except psycopg.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "An internal server error occurred"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@interest_groups.route("/members/<group_id>", methods=["GET"])
def get_members(group_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Get all members of the group
        cur.execute(
            """
            SELECT users.clerk_user_id, users.display_name, users.id
            FROM group_memberships
            JOIN users ON group_memberships.user_id = users.id
            WHERE group_memberships.group_id = %s
            """,
            (group_id,),
        )
        rows = cur.fetchall()
        members = [
            {"clerk_user_id": row[0], "display_name": row[1], "user_id": row[2]}
            for row in rows
        ]
        return jsonify({"members": members}), 200
    except psycopg.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "An internal server error occurred"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@interest_groups.route("/transfer_owner/<group_id>", methods=["POST"])
def transfer_owner(group_id):
    try:
        data = request.get_json(force=False, silent=False)
    except Exception as e:
        return jsonify({"error": "Invalid JSON", "details": str(e)}), 400

    if not data:
        return jsonify({"error": "No data provided"}), 400

    clerk_user_id = data.get("clerk_user_id")
    transfer_user_uuid = data.get("transfer_user_uuid")
    if not clerk_user_id or not isinstance(clerk_user_id, str):
        return jsonify({"error": "No user id provided / Invalid user id type"}), 400
    if not transfer_user_uuid or not isinstance(transfer_user_uuid, str):
        return (
            jsonify({"error": "No transfer user uuid provided / Invalid user id type"}),
            400,
        )

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 1. Get UUID for the current user (creator)
        cur.execute("SELECT id FROM users WHERE clerk_user_id = %s", (clerk_user_id,))
        user_row = cur.fetchone()
        if not user_row:
            return jsonify({"error": "User does not exist"}), 404
        user_uuid = user_row[0]

        # 2. Check group exists and get current creator
        cur.execute("SELECT creator_id FROM interest_groups WHERE id = %s", (group_id,))
        group_row = cur.fetchone()
        if not group_row:
            return jsonify({"error": "Group does not exist"}), 404
        creator_uuid = group_row[0]

        # 3. Check if current user is the creator
        if creator_uuid != user_uuid:
            return jsonify({"error": "User is not the creator of this group"}), 403

        # 4. Check if transfer user is a member
        cur.execute(
            "SELECT id FROM group_memberships WHERE user_id = %s AND group_id = %s",
            (transfer_user_uuid, group_id),
        )
        if not cur.fetchone():
            return (
                jsonify({"error": "Transfer user is not a member of this group"}),
                409,
            )

        # 5. Update group creator
        cur.execute(
            "UPDATE interest_groups SET creator_id = %s WHERE id = %s",
            (transfer_user_uuid, group_id),
        )
        conn.commit()
        return jsonify({"message": "Ownership successfully transferred"}), 200

    except psycopg.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "An internal server error occurred"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@interest_groups.route("/creator/<group_id>", methods=["GET"])
def get_creator(group_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Get the creator's UUID
        cur.execute("SELECT creator_id FROM interest_groups WHERE id = %s", (group_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Group does not exist"}), 404
        creator_uuid = row[0]
        # Get the creator's Clerk ID
        cur.execute("SELECT clerk_user_id FROM users WHERE id = %s", (creator_uuid,))
        user_row = cur.fetchone()
        if not user_row:
            return jsonify({"error": "Creator user does not exist"}), 404
        return jsonify({"creator_clerk_user_id": user_row[0]}), 200
    except psycopg.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "An internal server error occurred"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@interest_groups.route("/edit/<group_id>", methods=["PATCH"])
def edit_group(group_id):
    try:
        data = request.get_json(force=False, silent=False)
    except Exception as e:
        return jsonify({"error": "Invalid JSON", "details": str(e)}), 400

    if not data:
        return jsonify({"error": "No data provided"}), 400

    clerk_user_id = data.get("clerk_user_id")
    if not clerk_user_id or not isinstance(clerk_user_id, str):
        return jsonify({"error": "No user id provided / Invalid user id type"}), 400

    # Only allow certain fields to be updated
    allowed_fields = {"name", "description", "image_url"}
    updates = {k: v for k, v in data.items() if k in allowed_fields}

    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 1. Get user UUID and role
        cur.execute(
            "SELECT id, role FROM users WHERE clerk_user_id = %s", (clerk_user_id,)
        )
        user_row = cur.fetchone()
        if not user_row:
            return jsonify({"error": "User does not exist"}), 404
        user_uuid, user_role = user_row

        # 2. Get group creator
        cur.execute("SELECT creator_id FROM interest_groups WHERE id = %s", (group_id,))
        group_row = cur.fetchone()
        if not group_row:
            return jsonify({"error": "Group does not exist"}), 404
        creator_uuid = group_row[0]

        # 3. Admin check: must be site admin or group creator
        if user_role != "Admin" and user_uuid != creator_uuid:
            return jsonify({"error": "Not authorized"}), 403

        # 4. Build update query
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [group_id]
        cur.execute(f"UPDATE interest_groups SET {set_clause} WHERE id = %s", values)
        conn.commit()
        return jsonify({"message": "Group updated successfully"}), 200

    except psycopg.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "An internal server error occurred"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@interest_groups.route("/apply", methods=["POST"])
def apply_interest_group():
    try:
        data = request.get_json(force=False, silent=False)
    except Exception as e:
        return jsonify({"error": "Invalid JSON", "details": str(e)}), 400

    required_fields = ["clerk_user_id", "name", "description"]
    if not data or not all(f in data for f in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    clerk_user_id = data["clerk_user_id"]
    name = data["name"]
    description = data["description"]
    image_url = data.get("image_url")

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Get applicant's UUID
        cur.execute("SELECT id FROM users WHERE clerk_user_id = %s", (clerk_user_id,))
        user_row = cur.fetchone()
        if not user_row:
            return jsonify({"error": "User does not exist"}), 404
        applicant_id = user_row[0]

        # Insert application
        cur.execute(
            """
            INSERT INTO interest_group_applications (applicant_id, name, description, image_url)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (applicant_id, name, description, image_url),
        )
        app_id = cur.fetchone()[0]
        conn.commit()
        return (
            jsonify({"message": "Application submitted", "application_id": app_id}),
            201,
        )
    except psycopg.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "An internal server error occurred"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@interest_groups.route("/applications", methods=["GET"])
def list_applications():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT iga.id, u.display_name AS applicant_name, iga.name, iga.description, iga.status, iga.created_at
            FROM interest_group_applications iga
            JOIN users u ON iga.applicant_id = u.id
            ORDER BY iga.created_at DESC
        """
        )
        rows = cur.fetchall()
        applications = [
            {
                "id": row[0],
                "applicant_name": row[1],
                "name": row[2],
                "description": row[3],
                "status": row[4],
                "created_at": row[5],
            }
            for row in rows
        ]
        return jsonify({"applications": applications}), 200
    except psycopg.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "An internal server error occurred"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@interest_groups.route("/application/<application_id>", methods=["GET"])
def get_application(application_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT iga.id, u.display_name AS applicant_name, iga.name, iga.description, iga.status, iga.created_at, iga.image_url
            FROM interest_group_applications iga
            JOIN users u ON iga.applicant_id = u.id
            WHERE iga.id = %s
        """,
            (application_id,),
        )
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Application not found"}), 404
        application = {
            "id": row[0],
            "applicant_name": row[1],
            "name": row[2],
            "description": row[3],
            "status": row[4],
            "created_at": row[5],
            "image_url": row[6],
        }
        return jsonify(application), 200
    except psycopg.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "An internal server error occurred"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@interest_groups.route("/application/<application_id>/approve", methods=["POST"])
def approve_application(application_id):
    try:
        data = request.get_json(force=False, silent=False)
    except Exception as e:
        return jsonify({"error": "Invalid JSON", "details": str(e)}), 400

    admin_clerk_user_id = data.get("clerk_user_id")
    if not admin_clerk_user_id or not isinstance(admin_clerk_user_id, str):
        return (
            jsonify({"error": "No admin user id provided / Invalid user id type"}),
            400,
        )

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # 1. Get admin's UUID and check role
        cur.execute(
            "SELECT id, role FROM users WHERE clerk_user_id = %s",
            (admin_clerk_user_id,),
        )
        admin_row = cur.fetchone()
        if not admin_row:
            return jsonify({"error": "Admin user does not exist"}), 404
        admin_uuid, admin_role = admin_row
        if admin_role != "Admin":
            return jsonify({"error": "Not authorized"}), 403

        # 2. Get application details
        cur.execute(
            """
            SELECT applicant_id, name, description, image_url, status
            FROM interest_group_applications
            WHERE id = %s
        """,
            (application_id,),
        )
        app_row = cur.fetchone()
        if not app_row:
            return jsonify({"error": "Application not found"}), 404
        applicant_id, name, description, image_url, status = app_row
        if status != "pending":
            return jsonify({"error": "Application already processed"}), 400

        # 3. Create the interest group
        cur.execute(
            """
            INSERT INTO interest_groups (name, description, creator_id, image_url)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """,
            (name, description, applicant_id, image_url),
        )
        group_id = cur.fetchone()[0]

        # 4. Add applicant as a member
        cur.execute(
            """
            INSERT INTO group_memberships (user_id, group_id, role)
            VALUES (%s, %s, 'admin')
        """,
            (applicant_id, group_id),
        )

        # 5. Update application status
        cur.execute(
            """
            UPDATE interest_group_applications
            SET status = 'approved', admin_id = %s, reviewed_at = NOW()
            WHERE id = %s
        """,
            (admin_uuid, application_id),
        )

        conn.commit()
        return (
            jsonify(
                {
                    "message": "Application approved and group created",
                    "group_id": group_id,
                }
            ),
            200,
        )
    except psycopg.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "An internal server error occurred"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@interest_groups.route("/application/<application_id>/reject", methods=["POST"])
def reject_application(application_id):
    try:
        data = request.get_json(force=False, silent=False)
    except Exception as e:
        return jsonify({"error": "Invalid JSON", "details": str(e)}), 400

    admin_clerk_user_id = data.get("clerk_user_id")
    if not admin_clerk_user_id or not isinstance(admin_clerk_user_id, str):
        return (
            jsonify({"error": "No admin user id provided / Invalid user id type"}),
            400,
        )

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # 1. Get admin's UUID and check role
        cur.execute(
            "SELECT id, role FROM users WHERE clerk_user_id = %s",
            (admin_clerk_user_id,),
        )
        admin_row = cur.fetchone()
        if not admin_row:
            return jsonify({"error": "Admin user does not exist"}), 404
        admin_uuid, admin_role = admin_row
        if admin_role != "Admin":
            return jsonify({"error": "Not authorized"}), 403

        # 2. Get application details
        cur.execute(
            """
            SELECT status
            FROM interest_group_applications
            WHERE id = %s
        """,
            (application_id,),
        )
        app_row = cur.fetchone()
        if not app_row:
            return jsonify({"error": "Application not found"}), 404
        status = app_row[0]
        if status != "pending":
            return jsonify({"error": "Application already processed"}), 400

        # 3. Update application status to rejected
        cur.execute(
            """
            UPDATE interest_group_applications
            SET status = 'rejected', admin_id = %s, reviewed_at = NOW()
            WHERE id = %s
        """,
            (admin_uuid, application_id),
        )

        conn.commit()
        return (
            jsonify(
                {
                    "message": "Application rejected",
                    "application_id": application_id,
                }
            ),
            200,
        )
    except psycopg.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "An internal server error occurred"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
