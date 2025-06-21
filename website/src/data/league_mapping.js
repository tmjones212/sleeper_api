// Dynamic league mapping generated from API cache
// This replaces hardcoded league_id to year mappings
// Regenerate by running: python -c "import json; data=json.load(open('data/api_cache.json')); print('\n'.join(f'    \"{v[\"season\"]}\": \"{k.replace(\"league_\", \"\")}\",  // {v[\"name\"]}' for k,v in data.items() if k.startswith('league_')))"
const LEAGUE_MAPPING = {
    "2022": "839251409999347712",
    "2023": "916445745966915584",
    "2024": "1048308938824937472",
    "2025": "1181025001438806016",
};

function getLeagueIdForYear(year) {
    return LEAGUE_MAPPING[year] || null;
}
