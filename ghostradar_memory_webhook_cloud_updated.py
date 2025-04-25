
from flask import Flask, request, jsonify
from datetime import datetime
import json
import os
import requests

app = Flask(__name__)

# JSONBin setup with new Bin ID
BIN_ID = "680b7e048a456b79669119c3"
X_MASTER_KEY = "$2a$10$MQ.B4plEHGlX6FgQDNyDzu8fE/eGUI7fFBqVFSZTzjI4IYSeG2TP6"
JSONBIN_URL = f"https://api.jsonbin.io/v3/bins/{BIN_ID}"

# Write event to JSONBin
def append_to_jsonbin(entry):
    try:
        response = requests.get(JSONBIN_URL, headers={"X-Master-Key": X_MASTER_KEY})
        if response.status_code == 200:
            data = response.json()
            data["logs"].append(entry)
            # PUT the updated logs back into the bin
            requests.put(JSONBIN_URL, headers={"X-Master-Key": X_MASTER_KEY}, json=data)
        else:
            print("Error fetching bin data:", response.text)
    except Exception as e:
        print("Error writing to JSONBin:", e)

@app.route("/", methods=["GET"])
def health():
    return "GhostRadar Webhook is alive!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("🔔 Incoming Event")

        # Save the event to JSONBin
        append_to_jsonbin(data)

        return jsonify({"status": "received"}), 200
    except Exception as e:
        print("Error in webhook:", e)
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

