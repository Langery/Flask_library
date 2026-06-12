from flask import Blueprint

pages_blue = Blueprint('pages', __name__)

from blueprintStore.pages import routes
