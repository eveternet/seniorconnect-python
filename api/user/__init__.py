from flask import Blueprint

user = Blueprint('user', __name__)

from api.user.interest_groups import interest_groups

user_blueprints = [
    interest_groups,
]
            
for blueprint in user_blueprints:
    user.register_blueprint(blueprint)
 