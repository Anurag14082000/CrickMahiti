from flask import Flask, request, jsonify
import json
import os
import requests

app = Flask(__name__)

# ✅ Load static player stats from local JSON
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'cricket_data.json')
    with open(file_path, 'r') as file:
        return json.load(file)

cricket_data = load_data()

# ✅ Your CricketData.org API Key
API_KEY = "58b4bdc9-9091-4d97-92e5-fa2f2be4d434"

# ✅ Fetch LIVE data from cricketdata.org
def fetch_live_cricket_data(team_name):
    url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            matches = data.get("data", [])

            for match in matches:
                teams = match.get("name", "").lower()
                if team_name.lower() in teams:
                    team1 = match.get("teamInfo", [{}])[0].get("name", "Team A")
                    team2 = match.get("teamInfo", [{}])[1].get("name", "Team B")
                    status = match.get("status", "No status available")
                    score_list = match.get("score", [])

                    scores = []
                    for s in score_list:
                        scores.append(f"{s.get('inning', '')}: {s.get('r', '')}/{s.get('w', '')} in {s.get('o', '')} overs")

                    score_text = "; ".join(scores) if scores else "Score not available"
                    return f"{team1} vs {team2} — {status}. Scores: {score_text}"

            return f"No live match found for {team_name}."
        else:
            return f"Failed to fetch live data. Status code: {response.status_code}"
    
    except Exception as e:
        return f"Error fetching live score: {str(e)}"

# ✅ Unified stat handler
def get_player_stat(player, stat_type):
    player = player.strip().title()
    stat_type = stat_type.strip().lower()

    if stat_type == "live":
        return fetch_live_cricket_data(player)

    if player in cricket_data:
        stats = cricket_data[player]
        if stat_type in stats:
            value = stats[stat_type]
            return f"{player}'s {stat_type} is {value}."
        else:
            return f"Sorry, I don't have '{stat_type}' info for {player}."
    else:
        return f"Sorry, I don't have data for '{player}'."

# ✅ Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    player = req['queryResult']['parameters'].get('player')
    stat_type = req['queryResult']['parameters'].get('stat_type')

    response_text = get_player_stat(player, stat_type)
    return jsonify({"fulfillmentText": response_text})

if __name__ == '__main__':
    app.run(port=5000, debug=True)