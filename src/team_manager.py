from typing import Dict, List, Optional

class TeamManager:
	def __init__(self):
		self.team_aliases = {
			'tmjones212': ['trent', 'tjones', 'tmjones212','jj mccarthy waiting room'],
			'baodown': ['evan', 'baodown','Dark wings, dark words'],
			'halteclere': ['michael', 'halteclere'],
			'emanueljd3': ['emanueljd3', 'joey'],
			'EBao': ['EBao', 'eric'],
			'connerstafford11': ['connerstafford11', 'conner'],
			'lamjohnson56': ['lamjohnson56', 'johnson'],
			'ShadyCommish88': ['ShadyCommish88', 'pat','patrick'],
			'jake_the_snake': ['jake_the_snake', 'jake'],
			'androooooo': ['androooooo', 'andrew'],
			'mlum20': ['mlum20', 'lum'],
			'caviar89': ['caviar89', 'stan']
			# Add more team aliases as needed
		}
		
		# Create reverse lookup for easier searching
		self.team_name_to_primary = {}
		for primary, aliases in self.team_aliases.items():
			for alias in aliases:
				self.team_name_to_primary[alias.lower()] = primary
	
	def get_primary_name(self, team_name: str) -> Optional[str]:
		"""Get the primary team name from any alias."""
		return self.team_name_to_primary.get(team_name.lower())
	
	def get_all_aliases(self, team_name: str) -> List[str]:
		"""Get all aliases for a team (including primary name)."""
		primary_name = self.get_primary_name(team_name)
		return self.team_aliases.get(primary_name, []) if primary_name else []
	
	def is_same_team(self, name1: str, name2: str) -> bool:
		"""Check if two team names refer to the same team."""
		primary1 = self.get_primary_name(name1)
		primary2 = self.get_primary_name(name2)
		return primary1 is not None and primary1 == primary2 