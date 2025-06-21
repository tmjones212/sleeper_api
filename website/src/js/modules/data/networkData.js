/**
 * Network Data Module
 * Contains data for the trade network visualization
 */

export const networkData = {
    "biggest_trades": [],
    "edges": {
        "('BaoDown', 'EBao')": {
            "total_picks": 0,
            "total_players": 8,
            "trades": [
                {
                    "date": "2024-11-03 09:00 AM",
                    "details": {
                        "teams": [
                            {
                                "gives": {
                                    "draft_picks": [],
                                    "faab": [],
                                    "players": [
                                        {
                                            "player": "MIKE WILLIAMS",
                                            "player_id": "4068",
                                            "to_team": "Halteclere"
                                        }
                                    ]
                                },
                                "receives": {
                                    "draft_picks": [],
                                    "faab": [],
                                    "players": [
                                        {
                                            "from_team": "EBao",
                                            "player": "DEVIN SINGLETARY",
                                            "player_id": "6130"
                                        }
                                    ]
                                },
                                "team": "BaoDown"
                            },
                            {
                                "gives": {
                                    "draft_picks": [],
                                    "faab": [],
                                    "players": [
                                        {
                                            "player": "DEVIN SINGLETARY",
                                            "player_id": "6130",
                                            "to_team": "BaoDown"
                                        }
                                    ]
                                },
                                "receives": {
                                    "draft_picks": [],
                                    "faab": [],
                                    "players": [
                                        {
                                            "from_team": "Halteclere",
                                            "player": "JAHAN DOTSON",
                                            "player_id": "8119"
                                        }
                                    ]
                                },
                                "team": "EBao"
                            },
                            {
                                "gives": {
                                    "draft_picks": [],
                                    "faab": [],
                                    "players": [
                                        {
                                            "player": "JAHAN DOTSON",
                                            "player_id": "8119",
                                            "to_team": "EBao"
                                        }
                                    ]
                                },
                                "receives": {
                                    "draft_picks": [],
                                    "faab": [],
                                    "players": [
                                        {
                                            "from_team": "BaoDown",
                                            "player": "MIKE WILLIAMS",
                                            "player_id": "4068"
                                        }
                                    ]
                                },
                                "team": "Halteclere"
                            }
                        ],
                        "total_picks": 0,
                        "total_players": 6,
                        "trade_type": "players_only"
                    }
                },
                {
                    "date": "2022-10-25 12:52 PM",
                    "details": {
                        "teams": [
                            {
                                "gives": {
                                    "draft_picks": [
                                        {
                                            "from_team": "BaoDown",
                                            "image_url": "https://sleepercdn.com/content/nfl/players/11581.jpg",
                                            "original_owner": "BaoDown",
                                            "pick_number": 27,
                                            "player_id": "11581",
                                            "player_name": "MARSHAWN LLOYD",
                                            "position": "RB",
                                            "round": 3,
                                            "season": "2024",
                                            "to_team": "EBao",
                                            "type": "draft_pick"
                                        }
                                    ],
                                    "faab": [],
                                    "players": [
                                        {
                                            "player": "RASHAAD PENNY",
                                            "player_id": "4985",
                                            "to_team": "EBao"
                                        }
                                    ]
                                },
                                "receives": {
                                    "draft_picks": [
                                        {
                                            "from_team": "EBao",
                                            "image_url": "https://sleepercdn.com/content/nfl/players/11596.jpg",
                                            "original_owner": "EBao",
                                            "pick_number": 30,
                                            "player_id": "11596",
                                            "player_name": "BEN SINNOTT",
                                            "position": "TE",
                                            "round": 3,
                                            "season": "2024",
                                            "to_team": "BaoDown",
                                            "type": "draft_pick"
                                        }
                                    ],
                                    "faab": [],
                                    "players": []
                                },
                                "team": "BaoDown"
                            },
                            {
                                "gives": {
                                    "draft_picks": [
                                        {
                                            "from_team": "EBao",
                                            "image_url": "https://sleepercdn.com/content/nfl/players/11596.jpg",
                                            "original_owner": "EBao",
                                            "pick_number": 30,
                                            "player_id": "11596",
                                            "player_name": "BEN SINNOTT",
                                            "position": "TE",
                                            "round": 3,
                                            "season": "2024",
                                            "to_team": "BaoDown",
                                            "type": "draft_pick"
                                        }
                                    ],
                                    "faab": [],
                                    "players": []
                                },
                                "receives": {
                                    "draft_picks": [
                                        {
                                            "from_team": "BaoDown",
                                            "image_url": "https://sleepercdn.com/content/nfl/players/11581.jpg",
                                            "original_owner": "BaoDown",
                                            "pick_number": 27,
                                            "player_id": "11581",
                                            "player_name": "MARSHAWN LLOYD",
                                            "position": "RB",
                                            "round": 3,
                                            "season": "2024",
                                            "to_team": "EBao",
                                            "type": "draft_pick"
                                        }
                                    ],
                                    "faab": [],
                                    "players": [
                                        {
                                            "from_team": "BaoDown",
                                            "player": "RASHAAD PENNY",
                                            "player_id": "4985"
                                        }
                                    ]
                                },
                                "team": "EBao"
                            }
                        ],
                        "total_picks": 4,
                        "total_players": 2,
                        "trade_type": "mixed"
                    }
                }
            ],
            "weight": 2
        }
        // NOTE: This is a truncated example. The full networkData object is much larger.
        // In production, this should be loaded from a JSON file or API endpoint.
    },
    "nodes": {
        "BaoDown": {
            "avg_picks_per_trade": 0.0,
            "avg_players_per_trade": 1.05,
            "draft_picks_acquired": 0,
            "draft_picks_given": 0,
            "most_frequent_partner": "ShadyCommish88",
            "partners": [
                "EBao",
                "Halteclere",
                "ShadyCommish88",
                "androooooo",
                "emanueljd3",
                "lamjohnson56",
                "tmjones212"
            ],
            "players_acquired": 25,
            "players_given": 24,
            "total_trades": 24
        },
        "EBao": {
            "avg_picks_per_trade": 0.0,
            "avg_players_per_trade": 0.87,
            "draft_picks_acquired": 0,
            "draft_picks_given": 0,
            "most_frequent_partner": "ShadyCommish88",
            "partners": [
                "BaoDown",
                "Halteclere",
                "ShadyCommish88",
                "androooooo",
                "caviar89",
                "connerstafford11",
                "emanueljd3",
                "lamjohnson56",
                "tmjones212"
            ],
            "players_acquired": 36,
            "players_given": 36,
            "total_trades": 42
        },
        "Halteclere": {
            "avg_picks_per_trade": 0.0,
            "avg_players_per_trade": 0.53,
            "draft_picks_acquired": 0,
            "draft_picks_given": 0,
            "most_frequent_partner": "ShadyCommish88",
            "partners": [
                "BaoDown",
                "EBao",
                "ShadyCommish88",
                "caviar89",
                "connerstafford11",
                "emanueljd3",
                "lamjohnson56",
                "tmjones212"
            ],
            "players_acquired": 10,
            "players_given": 19,
            "total_trades": 19
        },
        "ShadyCommish88": {
            "avg_picks_per_trade": 0.0,
            "avg_players_per_trade": 0.97,
            "draft_picks_acquired": 0,
            "draft_picks_given": 0,
            "most_frequent_partner": "EBao",
            "partners": [
                "BaoDown",
                "EBao",
                "Halteclere",
                "androooooo",
                "caviar89",
                "connerstafford11",
                "emanueljd3",
                "lamjohnson56",
                "tmjones212"
            ],
            "players_acquired": 78,
            "players_given": 77,
            "total_trades": 80
        },
        "androooooo": {
            "avg_picks_per_trade": 0.0,
            "avg_players_per_trade": 0.72,
            "draft_picks_acquired": 0,
            "draft_picks_given": 0,
            "most_frequent_partner": "ShadyCommish88",
            "partners": [
                "BaoDown",
                "EBao",
                "ShadyCommish88",
                "caviar89",
                "emanueljd3"
            ],
            "players_acquired": 13,
            "players_given": 13,
            "total_trades": 18
        },
        "caviar89": {
            "avg_picks_per_trade": 0.0,
            "avg_players_per_trade": 0.47,
            "draft_picks_acquired": 0,
            "draft_picks_given": 0,
            "most_frequent_partner": "ShadyCommish88",
            "partners": [
                "EBao",
                "Halteclere",
                "ShadyCommish88",
                "androooooo",
                "emanueljd3"
            ],
            "players_acquired": 8,
            "players_given": 9,
            "total_trades": 17
        },
        "connerstafford11": {
            "avg_picks_per_trade": 0.0,
            "avg_players_per_trade": 0.45,
            "draft_picks_acquired": 0,
            "draft_picks_given": 0,
            "most_frequent_partner": "ShadyCommish88",
            "partners": [
                "EBao",
                "Halteclere",
                "ShadyCommish88"
            ],
            "players_acquired": 5,
            "players_given": 5,
            "total_trades": 11
        },
        "emanueljd3": {
            "avg_picks_per_trade": 0.0,
            "avg_players_per_trade": 0.97,
            "draft_picks_acquired": 0,
            "draft_picks_given": 0,
            "most_frequent_partner": "ShadyCommish88",
            "partners": [
                "BaoDown",
                "EBao",
                "Halteclere",
                "ShadyCommish88",
                "androooooo",
                "caviar89",
                "lamjohnson56",
                "tmjones212"
            ],
            "players_acquired": 36,
            "players_given": 36,
            "total_trades": 37
        },
        "lamjohnson56": {
            "avg_picks_per_trade": 0.0,
            "avg_players_per_trade": 1.42,
            "draft_picks_acquired": 0,
            "draft_picks_given": 0,
            "most_frequent_partner": "emanueljd3",
            "partners": [
                "BaoDown",
                "EBao",
                "Halteclere",
                "ShadyCommish88",
                "emanueljd3"
            ],
            "players_acquired": 19,
            "players_given": 19,
            "total_trades": 14
        },
        "tmjones212": {
            "avg_picks_per_trade": 0.0,
            "avg_players_per_trade": 0.5,
            "draft_picks_acquired": 0,
            "draft_picks_given": 0,
            "most_frequent_partner": "ShadyCommish88",
            "partners": [
                "BaoDown",
                "EBao",
                "Halteclere",
                "ShadyCommish88",
                "emanueljd3"
            ],
            "players_acquired": 6,
            "players_given": 6,
            "total_trades": 12
        }
    }
};