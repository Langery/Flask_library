from flask import Blueprint

pages_blue = Blueprint('pages', __name__, url_prefix='/api')

from blueprintStore.pages import routes
