from flask import Blueprint

auth_blue = Blueprint('auth', __name__)

from blueprintStore.auth import routes
