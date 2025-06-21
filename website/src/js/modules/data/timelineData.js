/**
 * Timeline Data Module
 * Contains data for the trade timeline visualization
 */

export const timelineData = {
    "busiest_periods": [],
    "monthly_breakdown": {
        "2022-07": 1,
        "2022-08": 5,
        "2022-09": 7,
        "2022-10": 3,
        "2022-11": 2,
        "2022-12": 4,
        "2023-01": 2,
        "2023-02": 1,
        "2023-03": 2,
        "2023-04": 5,
        "2023-05": 12,
        "2023-06": 2,
        "2023-07": 1,
        "2023-09": 4,
        "2023-10": 9,
        "2023-11": 10,
        "2024-01": 10,
        "2024-03": 2,
        "2024-04": 1,
        "2024-05": 9,
        "2024-07": 4,
        "2024-08": 5,
        "2024-09": 5,
        "2024-10": 5,
        "2024-11": 10,
        "2024-12": 7,
        "2025-01": 3,
        "2025-02": 2,
        "2025-03": 1,
        "2025-04": 11,
        "2025-05": 4,
        "2025-06": 9
    },
    "stats": {
        "most_active_month": "2023-05",
        "total_picks_traded": 0,
        "total_players_traded": 538,
        "total_trades": 158,
        "trade_frequency": {}
    },
    "trades": [
        {
            "date": "2025-06-16 04:18 PM",
            "picks_count": 0,
            "players_count": 2,
            "teams_involved": ["Halteclere", "lamjohnson56"],
            "timestamp": 1750108681699,
            "trade_details": {
                "teams": [
                    {
                        "gives": {
                            "draft_picks": [],
                            "faab": [],
                            "players": [
                                {
                                    "player": "JAYLEN WADDLE",
                                    "player_id": "7526",
                                    "to_team": "Halteclere"
                                }
                            ]
                        },
                        "receives": {
                            "draft_picks": [
                                {
                                    "from_team": "Halteclere",
                                    "original_owner": "Halteclere",
                                    "round": 1,
                                    "season": "2028",
                                    "to_team": "lamjohnson56",
                                    "type": "draft_pick"
                                }
                            ],
                            "faab": [],
                            "players": []
                        },
                        "team": "lamjohnson56"
                    },
                    {
                        "gives": {
                            "draft_picks": [
                                {
                                    "from_team": "Halteclere",
                                    "original_owner": "Halteclere",
                                    "round": 1,
                                    "season": "2028",
                                    "to_team": "lamjohnson56",
                                    "type": "draft_pick"
                                }
                            ],
                            "faab": [],
                            "players": []
                        },
                        "receives": {
                            "draft_picks": [],
                            "faab": [],
                            "players": [
                                {
                                    "from_team": "lamjohnson56",
                                    "player": "JAYLEN WADDLE",
                                    "player_id": "7526"
                                }
                            ]
                        },
                        "team": "Halteclere"
                    }
                ],
                "total_picks": 2,
                "total_players": 2,
                "trade_type": "mixed"
            },
            "trade_summary": "Halteclere received: JAYLEN WADDLE | lamjohnson56 gave: JAYLEN WADDLE"
        },
        {
            "date": "2025-06-16 01:13 AM",
            "picks_count": 0,
            "players_count": 4,
            "teams_involved": ["BaoDown", "lamjohnson56"],
            "timestamp": 1750054409800,
            "trade_details": {
                "teams": [
                    {
                        "gives": {
                            "draft_picks": [],
                            "faab": [],
                            "players": [
                                {
                                    "player": "MAC JONES",
                                    "player_id": "7527",
                                    "to_team": "BaoDown"
                                }
                            ]
                        },
                        "receives": {
                            "draft_picks": [],
                            "faab": [],
                            "players": [
                                {
                                    "from_team": "BaoDown",
                                    "player": "WILL LEVIS",
                                    "player_id": "9999"
                                }
                            ]
                        },
                        "team": "lamjohnson56"
                    },
                    {
                        "gives": {
                            "draft_picks": [],
                            "faab": [],
                            "players": [
                                {
                                    "player": "WILL LEVIS",
                                    "player_id": "9999",
                                    "to_team": "lamjohnson56"
                                }
                            ]
                        },
                        "receives": {
                            "draft_picks": [],
                            "faab": [],
                            "players": [
                                {
                                    "from_team": "lamjohnson56",
                                    "player": "MAC JONES",
                                    "player_id": "7527"
                                }
                            ]
                        },
                        "team": "BaoDown"
                    }
                ],
                "total_picks": 0,
                "total_players": 4,
                "trade_type": "players_only"
            },
            "trade_summary": "lamjohnson56 received: WILL LEVIS and gave: MAC JONES | BaoDown received: MAC JONES and gave: WILL LEVIS"
        }
        // NOTE: This is a truncated example. The full trades array contains many more entries.
        // In production, this should be loaded from a JSON file or API endpoint.
    ]
};