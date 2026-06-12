from flask import Blueprint

layout_blue = Blueprint('layout', __name__)

from blueprintStore.layout import routes
