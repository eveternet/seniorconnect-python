from flask import Blueprint

user = Blueprint("user", __name__)

from api.user.interest_groups import interest_groups

user.registerblueprint(interest_groups, url_prefix="/interest_groups")
