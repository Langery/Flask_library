from flask import Blueprint

library_blue = Blueprint('library', __name__)

from blueprintStore.library import routes
