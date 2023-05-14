from auction import app
from auction import socketio



if __name__ == '__main__':
    socketio.run(app,debug=True,allow_unsafe_werkzeug=True)
