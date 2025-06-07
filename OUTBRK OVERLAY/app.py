from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

API_URL = "https://api.outbrkgame.com/api/stats?token=YOUR TOKEN HERE"
TRACKED_STATS = [
    "distance_travelled_driving",
    "reports_sent_first",
    "tornado_direct_hits"
]

initial_values = {}
session_values = {
    "driving": 0,
    "first": 0,
    "hits": 0
}

def fetch_stats():
    try:
        response = requests.get(API_URL)
        data = response.json()
        stat_list = data["playerstats"]["stats"]
        return {s["name"]: s["value"] for s in stat_list if s["name"] in TRACKED_STATS}
    except Exception as e:
        print("Error fetching stats:", e)
        return {}

@app.route("/stats")
def stats():
    global initial_values, session_values

    current = fetch_stats()
    if not current:
        return jsonify({"hidden": True})

    if not initial_values:
        initial_values = current
        return jsonify({"hidden": True})

    # Compute session deltas
    session_values["driving"] += max(0, current["distance_travelled_driving"] - initial_values["distance_travelled_driving"]) * 0.621371
    session_values["first"] += max(0, current["reports_sent_first"] - initial_values["reports_sent_first"])
    session_values["hits"] += max(0, current["tornado_direct_hits"] - initial_values["tornado_direct_hits"])

    # Update initial values
    initial_values = current

    return jsonify({
        "driving": round(session_values["driving"]),
        "first": session_values["first"],
        "hits": session_values["hits"]
    })

@app.route("/reset")
def reset():
    global initial_values, session_values
    initial_values = {}
    session_values = {
        "driving": 0,
        "first": 0,
        "hits": 0
    }
    return "Reset complete"

@app.route("/")
def overlay():
    return render_template("overlay.html")

if __name__ == "__main__":
    app.run(debug=True)
