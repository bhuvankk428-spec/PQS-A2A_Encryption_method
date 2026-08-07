from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
)

def emit_log(event):
    socketio.emit(
        "protocol_event",
        event,
        namespace="/",
    )

@app.route("/")
def home():
    return "Quantum Secure Monitor Running"

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False,
    )