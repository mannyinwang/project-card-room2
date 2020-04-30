from config import app, socketio
import routes
from flask_socketio import SocketIO


if __name__ == '__main__':
    #socketio.run(app, debug=True)
    app.run(debug=True)