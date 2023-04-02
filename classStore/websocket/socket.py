from flask import Flask;
from flask_sockets import Sockets;

html = Blueprint(r'html', __name__);
ws = Blueprint(r'ws', __name__)；


app = Flask(__name__);
sockets = Sockets(app);

@sockets.route('/echo')
def echo_socket(ws):
    message = sockets.receive();
    while not ws.closed:
        message = ws.receive();
        ws.send(message);

app.register_blueprint(html, url_prefix=r'/');
sockets.register_blueprint(ws, url_prefix=r'/');

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('127.0.0.1', 5001), app, handler_class=WebSocketHandler)
    server.serve_forever()