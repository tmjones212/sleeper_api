from flask import Flask, jsonify, Response
from flask_cors import CORS
from client import SleeperAPI
from team_value_service import TeamValueService

app = Flask(__name__)
CORS(app)  # This allows your static site to call this API

@app.route('/api/team-values/<league_id>')
def get_team_values(league_id):
    client = SleeperAPI()
    service = TeamValueService(client)
    team_values = service.get_team_values(league_id)
    return jsonify(team_values)

if __name__ == '__main__':
    app.run(debug=True) 