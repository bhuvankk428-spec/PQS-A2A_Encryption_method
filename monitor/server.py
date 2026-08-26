from flask import Flask, request, jsonify
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

@app.route("/api/emit", methods=["POST"])
def relay_event():
    event = request.get_json(silent=True)

    if not event:
        return jsonify({"error": "invalid json"}), 400

    emit_log(event)

    return jsonify({"ok": True}), 200

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False,
    )
