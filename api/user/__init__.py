from flask import Blueprint

user = Blueprint("user", __name__)

from api.user.interest_groups import interest_groups

user.register_blueprint(interest_groups, url_prefix="/interest_groups")
print("a")
