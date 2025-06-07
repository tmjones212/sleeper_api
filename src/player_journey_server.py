#!/usr/bin/env python3
"""
Simple server to provide player journey data for the visualization
"""
import sys
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add src directory to path for imports
sys.path.append(os.path.dirname(__file__))

from client import SleeperAPI

app = Flask(__name__)
CORS(app)

# Initialize the API
api = None

def get_api():
    global api
    if api is None:
        api = SleeperAPI("1048308938824937472")
    return api

@app.route('/player_journey/<league_id>/<player_name>')
def get_player_journey(league_id, player_name):
    """Get comprehensive player journey data"""
    try:
        sleeper_api = get_api()
        journey_data = sleeper_api.get_player_trade_journey(player_name, league_id)
        return jsonify(journey_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("Starting Player Journey Server...")
    print("Server will be available at http://localhost:5000")
    app.run(debug=True, port=5000)