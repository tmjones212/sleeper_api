from flask import Flask, jsonify, Response, render_template, request
from flask_cors import CORS
from client import SleeperAPI
from team_value_service import TeamValueService
from matchup_service import MatchupService
from trade_visualization_service import LeagueVisualizationService

app = Flask(__name__, template_folder='../templates')
CORS(app)  # This allows your static site to call this API

@app.route('/api/team-values/<league_id>')
def get_team_values(league_id):
    client = SleeperAPI()
    service = TeamValueService(client)
    team_values = service.get_team_values(league_id)
    return jsonify(team_values)

@app.route('/matchups/<league_id>')
def matchups_page(league_id):
    """Render the matchups page for a specific league."""
    client = SleeperAPI()
    service = MatchupService(client)
    
    # Get query parameters
    year = request.args.get('year', type=int)
    week = request.args.get('week')
    
    # Convert week to int if it's not 'all'
    if week and week != 'all':
        try:
            week = int(week)
        except ValueError:
            week = None
    elif week == 'all':
        week = 'all'
    else:
        week = None
    
    try:
        matchup_data = service.get_matchup_data(league_id, year, week)
        return render_template('matchups.html', **matchup_data)
    except Exception as e:
        return f"Error loading matchups: {str(e)}", 500

@app.route('/api/matchups/<league_id>')
def get_matchups_api(league_id):
    """API endpoint for matchup data."""
    client = SleeperAPI()
    service = MatchupService(client)
    
    year = request.args.get('year', type=int)
    week = request.args.get('week')
    
    if week and week != 'all':
        try:
            week = int(week)
        except ValueError:
            week = None
    elif week == 'all':
        week = 'all'
    else:
        week = None
    
    try:
        matchup_data = service.get_matchup_data(league_id, year, week)
        return jsonify(matchup_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/league/<league_id>')
def league_visualization(league_id):
    """Render the complete league visualization page."""
    client = SleeperAPI()
    service = LeagueVisualizationService(client)
    
    try:
        html_content = service.generate_league_visualization_html(league_id)
        return Response(html_content, mimetype='text/html')
    except Exception as e:
        return f"Error loading league visualization: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True) 