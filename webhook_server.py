
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return "GhostRadar Webhook is alive!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("🔔 Incoming Event")

        signature = data.get("transaction", {}).get("signature", "N/A")
        timestamp = data.get("timestamp", int(datetime.now().timestamp()))
        time_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        transfers = data.get("events", {}).get("tokenTransfers", [])
        for t in transfers:
            amount = float(t.get("amount", 0))
            token = t.get("mint", "")[:6] + "..."
            sender = t.get("fromUserAccount", "")
            receiver = t.get("toUserAccount", "")
            sender_fmt = sender[:4] + "..." + sender[-4:] if sender else "N/A"
            receiver_fmt = receiver[:4] + "..." + receiver[-4:] if receiver else "N/A"

            print(f"""
🕒 {time_str}
🔗 Tx: https://solscan.io/tx/{signature}
💸 Amount: {amount}
🪙 Token Mint: {token}
🧍 From: {sender_fmt}
🧍 To:   {receiver_fmt}
-------------------------
""")

        return jsonify({"status": "received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
