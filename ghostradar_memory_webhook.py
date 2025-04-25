
from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)
LOG_FILE = "ghostlog.json"

def append_to_log(entry):
    try:
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                json.dump([], f)

        with open(LOG_FILE, "r") as f:
            data = json.load(f)

        data.append(entry)

        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Error writing to log:", e)

@app.route("/", methods=["GET"])
def health():
    return "GhostRadar Webhook is alive!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("🔔 Incoming Event")
        append_to_log(data)
        return jsonify({"status": "received"}), 200
    except Exception as e:
        print("Error in webhook:", e)
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
