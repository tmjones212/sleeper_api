import os
from client import SleeperAPI
from report_service import ReportService

def test_bench_players_stats(tmp_path):
    league_id = "1048308938824937472"
    client = SleeperAPI(league_id)
    report_service = ReportService(client)
    csv_filename = tmp_path / "bench_players_stats.csv"
    report_service.write_bench_players_stats_csv(league_id, csv_filename)

    # Assert the file was created and has content
    assert os.path.exists(csv_filename)
    with open(csv_filename, 'r') as f:
        lines = f.readlines()
    assert len(lines) > 1  # At least header + one row 