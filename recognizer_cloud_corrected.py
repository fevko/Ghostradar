
import requests
from datetime import datetime
import json
from collections import defaultdict  # <-- Adding missing import

# JSONBin setup with correct Bin ID and URL
BIN_ID = "680b7e048a456b79669119c3"
X_MASTER_KEY = "$2a$10$MQ.B4plEHGlX6FgQDNyDzu8fE/eGUI7fFBqVFSZTzjI4IYSeG2TP6"
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

# Fetch logs from JSONBin
def load_logs():
    try:
        response = requests.get(JSONBIN_URL, headers={"X-Master-Key": X_MASTER_KEY})
        if response.status_code == 200:
            data = response.json()
            return data["logs"]
        else:
            print("Error fetching bin data:", response.text)
            return []
    except Exception as e:
        print("Error reading from JSONBin:", e)
        return []

def format_wallet(w):
    return w[:4] + "..." + w[-4:] if w else "N/A"

def score_transaction(tx):
    score = 0
    transfers = tx.get("events", {}).get("tokenTransfers", [])
    score += len(transfers) * 5  # more transfers = stronger node activity
    for t in transfers:
        amt = float(t.get("amount", 0))
        if amt > 1000: score += 5
        if amt > 5000: score += 10
    return score

def detect_nodes(logs):
    token_activity = defaultdict(list)
    for tx in logs:
        signature = tx.get("transaction", {}).get("signature", "N/A")
        timestamp = tx.get("timestamp", int(datetime.now().timestamp()))
        transfers = tx.get("events", {}).get("tokenTransfers", [])
        for t in transfers:
            token = t.get("mint", "")[:6]
            token_activity[token].append({
                "timestamp": timestamp,
                "signature": signature,
                "amount": float(t.get("amount", 0)),
                "from": t.get("fromUserAccount", ""),
                "to": t.get("toUserAccount", ""),
                "score": score_transaction(tx)
            })

    # Detect forming nodes
    print("\n📡 NODE SCAN STARTED")
    for token, events in token_activity.items():
        if len(events) < 3:
            continue  # too little data
        events.sort(key=lambda x: x["timestamp"])
        last = events[-1]
        recent_events = [e for e in events if last["timestamp"] - e["timestamp"] < 300]  # last 5 minutes

        if len(recent_events) >= 3:
            avg_score = sum(e["score"] for e in recent_events) / len(recent_events)
            print(f"\n🧠 NODE DETECTED")
            print(f"- Token: {token}")
            print(f"- Events: {len(recent_events)} in 5 mins")
            print(f"- Avg Score: {round(avg_score, 1)}")
            print(f"- Last Tx: https://solscan.io/tx/{last['signature']}")
            print(f"- From: {format_wallet(last['from'])} → To: {format_wallet(last['to'])}")
            print(f"- Node Status: FORMING")
            print("-" * 40)

if __name__ == "__main__":
    logs = load_logs()
    detect_nodes(logs)
