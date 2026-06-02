from flask import Flask, Blueprint
from flask_sockets import Sockets


html_blue = Blueprint('html', __name__)
ws_blue = Blueprint('ws', __name__)

app = Flask(__name__)
sockets = Sockets(app)


@sockets.route('/echo')
def echo_socket(ws):
    message = sockets.receive()
    while not ws.closed:
        message = sockets.receive()
        ws.send(message)


app.register_blueprint(html_blue, url_prefix='/')
sockets.register_blueprint(ws_blue, url_prefix='/')


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('127.0.0.1', 5001), app, handler_class=WebSocketHandler)
    server.serve_forever()