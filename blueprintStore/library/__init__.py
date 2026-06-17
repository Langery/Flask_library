from flask import Blueprint

library_blue = Blueprint('library', __name__, url_prefix='/api')

from blueprintStore.library import routes
