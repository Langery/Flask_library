from flask import Blueprint

layout_blue = Blueprint('layout', __name__, url_prefix='/api')

from blueprintStore.layout import routes
