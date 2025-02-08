
import json

from sleeper_api_calls import get_player_stats_from_api


year = 2024
# positions = ["QB", "RB", "WR", "TE",'DB']
positions = ["QB", "RB", "TE",'DB']

for position in positions:
	for week in range(1,20):
		stats = get_player_stats_from_api(year, week, position)
		# Print stats in JSON format
		print(json.dumps(stats, indent=4))
		# Convert stats objects to dictionaries
		# stats_dict = {player_id: stat.__dict__ for player_id, stat in stats.items()}
		# Create filename with the specified pattern
		filename = f"{year}_Week_{week}_{position}.json"
		# Write stats to JSON file
		with open(filename, 'w') as f:
			json.dump(stats, f, indent=4)