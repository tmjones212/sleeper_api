class RosterDisplay:
    @staticmethod
    def print_league_rosters(league_manager, player_manager, league_id: str):
        league = league_service.get_league(league_id, fetch_all=True)
        players = player_service.players

        print(f"Rosters for {league.name}:")
        for team in league.teams:
            print(f"\n{team.display_name} ({team.team_name}):")
            if team.roster:
                RosterDisplay._print_roster_section(team.roster, players, player_manager)
            else:
                print("  No roster data available")
            print("---")

    @staticmethod
    def _print_roster_section(roster, players, player_manager):
        print("  Starters:")
        for player_id in roster.starters:
            RosterDisplay._print_player(players, player_id, "    ", player_manager)
        
        bench = set(roster.players) - set(roster.starters)
        if roster.reserve:
            bench -= set(roster.reserve)
        if roster.taxi:
            bench -= set(roster.taxi)
        
        if bench:
            print("  Bench:")
            for player_id in bench:
                RosterDisplay._print_player(players, player_id, "    ", player_manager)
        
        if roster.reserve:
            print("  IR:")
            for player_id in roster.reserve:
                RosterDisplay._print_player(players, player_id, "    ", player_manager)
        
        if roster.taxi:
            print("  Taxi Squad:")
            for player_id in roster.taxi:
                RosterDisplay._print_player(players, player_id, "    ", player_manager)

    @staticmethod
    def _print_player(players, player_id: str, indent: str, player_manager):
        player = players.get(player_id)
        if player:
            formatted_name = player_service.format_player_name(f"{player.first_name} {player.last_name}")
            print(f"{indent}- {formatted_name} ({player.position})")
        else:
            print(f"{indent}- Unknown Player (ID: {player_id})") 