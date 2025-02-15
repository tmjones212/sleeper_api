from typing import List, Dict, Any
import os
from jinja2 import Environment, FileSystemLoader
import webbrowser

from client import SleeperAPI

class DraftVisualizationService:
	def __init__(self, client):
		self.client = client
		self.default_player_image = "https://sleepercdn.com/images/v2/icons/player_default.webp"
		self.env = Environment(loader=FileSystemLoader('templates'))
	
	def generate_draft_board(self, draft_id: str, output_path: str = "draft_board.html"):
		"""Generate an HTML draft board visualization."""
		# Get draft data
		picks = self.client.draft_service.get_draft_picks(draft_id)
		draft_details = self.client.draft_service.get_draft_details(draft_id)
		
		# Get league data to map user IDs to team names
		league_id = draft_details.get('league_id')
		league = self.client.league_service.get_league(league_id, fetch_all=True)
		user_id_to_team = {
			team.user_id: team.display_name 
			for team in league.teams
		}
		
		# Calculate draft dimensions
		teams_count = len(draft_details.get('draft_order', {}))
		rounds = max(pick['round'] for pick in picks)
		
		# Get draft order and map to team names
		draft_order = draft_details.get('draft_order', {})
		team_headers = []
		for user_id, position in sorted(draft_order.items(), key=lambda x: x[1]):
			team_name = user_id_to_team.get(user_id, f"Team {position}")
			team_headers.append(team_name)
		
		# Organize picks into a 2D grid
		draft_grid = []
		for round_num in range(1, rounds + 1):
			round_picks = []
			for pick_num in range(1, teams_count + 1):
				pick = next(
					(p for p in picks 
					 if p['round'] == round_num and p['pick_in_round'] == pick_num),
					None
				)
				if pick:
					pick['image_url'] = self._get_player_image_url(pick['player_id'])
				round_picks.append(pick)
			draft_grid.append(round_picks)
		
		# Render template
		template = self.env.get_template('draft_board.html')
		html_content = template.render(
			draft_grid=draft_grid,
			rounds=rounds,
			teams_count=teams_count,
			default_image=self.default_player_image,
			team_order=team_headers  # Using the actual draft order
		)
		
		# Save to file
		with open(output_path, 'w', encoding='utf-8') as f:
			f.write(html_content)
		
		# Open the file in the default web browser
		webbrowser.open('file://' + os.path.abspath(output_path))
		
		return output_path
	
	def _get_player_image_url(self, player_id: str) -> str:
		"""Get the player's image URL from Sleeper."""
		return f"https://sleepercdn.com/content/nfl/players/{player_id}.jpg" 
		
if __name__ == "__main__":
	client = SleeperAPI()
	viz_service = DraftVisualizationService(client)
	
	# 2024 league ID
	league_id = "1048308938824937472"
	
	# Get the most recent draft for this league
	drafts = client.draft_service.get_league_drafts(league_id)
	if drafts:
		draft_id = drafts[0]['draft_id']
		html_path = viz_service.generate_draft_board(draft_id)
		print(f"Draft board generated at: {html_path}")
	else:
		print("No drafts found for this league")
