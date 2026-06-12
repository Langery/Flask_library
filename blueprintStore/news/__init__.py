from flask import Blueprint

news_blue = Blueprint('news', __name__)

from blueprintStore.news import routes
