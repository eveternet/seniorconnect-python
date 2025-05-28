from flask import Blueprint

user_blueprints = Blueprint("user", __name__)

from api.user.interest_groups import interest_groups
from api.user.auth import authUser

user_blueprints.register_blueprint(interest_groups, url_prefix="/interest_groups")
user_blueprints.register_blueprint(authUser, url_prefix="/auth")
