
# Importance
Every question I ask is extremely important and my family's livelihood is on the line.

Do a commit when you make changes.

Whenever you learn something important about the codebase that would be useful to know in the future, store it here.

## Recent Learnings

### Draft Pick Display Issue (Fixed)
- **Issue**: Some draft picks were showing as generic "2028 Round 1 pick" instead of "Halteclere's 2028 Round 1 pick"
- **Root Cause**: The transaction service was correctly setting `original_owner` using `roster_id`, but the HTML needed to be regenerated
- **Fix**: Simply regenerating the HTML with `python src/update_index.py` resolved the issue
- **Key Insight**: The data processing and template logic were correct; it was just a matter of regenerating the output

### Code Structure
- **Transaction Service**: Correctly uses `roster_id` to determine original draft pick owner
- **Template Logic**: Has proper fallback logic for displaying picks with/without ownership
- **Trade Data Structure**: Uses `team_assets` structure with `receives`/`gives` arrays containing draft pick objects


# Draft Pick Ownership Fix Documentation

## Issue Description
Draft picks in trade history were showing as generic "2028 Round 1 pick" instead of displaying the original owner like "Halteclere's 2028 Round 1 pick".

## Root Cause Analysis

### 1. **Data Structure Problem**
The transaction service was incorrectly using `previous_owner_id` to determine `original_owner` instead of using `roster_id` (which represents the original draft position).

**Wrong Logic:**
```python
'original_owner': from_team  # from_team was derived from previous_owner_id
```

**Correct Logic:**
```python
original_roster_id = pick.get('roster_id', pick['previous_owner_id'])
original_owner = self._get_historical_team_name(original_roster_id, pick['season'], league_id, roster_to_team)
'original_owner': original_owner
```

### 2. **Template Logic Problem**
The Jinja2 template had insufficient fallback logic for displaying picks without ownership:

**Wrong Template:**
```html
{{ pick.original_owner }}'s {{ pick.season }} Round {{ pick.round }} pick
```
This would show `'s 2028 Round 1 pick` if `original_owner` was None/empty.

**Fixed Template:**
```html
{% if pick.pick_number and pick.player_name %}
    Pick #{{ pick.pick_number }} ({{ pick.original_owner }}'s {{ pick.season }} R{{ pick.round }}) - {{ pick.player_name }}
{% elif pick.original_owner %}
    {{ pick.original_owner }}'s {{ pick.season }} Round {{ pick.round }} pick
{% else %}
    {{ pick.season }} Round {{ pick.round }} pick
{% endif %}
```

### 3. **Timeline Data Processing Problem**
The `get_league_trade_timeline` method was counting picks using the old `received/given` structure instead of the new `team_assets` structure:

**Wrong Counting:**
```python
picks_count = len(trade.get('received', {}).get('draft_picks', []))
```

**Fixed Counting:**
```python
if 'team_assets' in trade:
    for team_name, assets in trade['team_assets'].items():
        for direction in ['receives', 'gives']:
            if direction in assets:
                for asset in assets[direction]:
                    if asset.get('type') == 'draft_pick':
                        picks_count += 1
```

## Files Modified

### 1. `/src/transaction_service.py`
- **Lines 185-187**: Added logic to determine original owner using `roster_id`
- **Lines 360-362**: Fixed same issue in `get_trades_by_manager` method

### 2. `/templates/trade_visualization.html`  
- **Line 905**: Added proper fallback logic for pick display

### 3. `/src/trade_visualization_service.py`
- **Lines 401-417**: Fixed pick counting to use `team_assets` structure

## Data Structure Explanation

### Draft Pick Fields:
- `roster_id`: Original draft position (who the pick originally belonged to)
- `previous_owner_id`: Who owned the pick immediately before this trade
- `owner_id`: Who owns the pick after this trade

### Example:
```json
{
  "round": 1,
  "season": "2028", 
  "roster_id": 4,        // Halteclere's original pick
  "owner_id": 8,         // lamjohnson56 gets it
  "previous_owner_id": 4 // Halteclere had it before
}
```

For original owner display, we should use `roster_id` (4 → "Halteclere"), not `previous_owner_id`.

## Testing Commands

To verify the fix works:

```bash
# Regenerate trade data
python src/update_index.py

# Check that picks show ownership
grep -A 5 -B 5 "Round.*pick" index.html

# Verify timeline data includes picks
python3 -c "
import sys
sys.path.append('./src')
from trade_visualization_service import LeagueVisualizationService
from client import SleeperAPI
service = LeagueVisualizationService(SleeperAPI('1181025001438806016'))
timeline = service.get_league_trade_timeline('1181025001438806016')
print(f'Total picks in timeline: {timeline[\"stats\"][\"total_picks_traded\"]}')
"
```

## Prevention Notes

1. **Always use `roster_id` for original ownership** - this represents the draft slot/position
2. **Use `previous_owner_id` only for trade flow** - this shows who had it before the current trade
3. **Test both template rendering AND JavaScript data** - the site uses multiple data structures
4. **Check both `team_assets` and legacy `received/given` structures** when processing trades
5. **Always include fallback logic in templates** for missing data fields

## Commands to Fix Similar Issues

If you encounter similar pick ownership issues:

1. **Debug the data structure:**
```python
# Check what the pick data looks like
python3 -c "
from src.transaction_service import TransactionService
from src.client import SleeperAPI
service = TransactionService(SleeperAPI('LEAGUE_ID'))
trades = service.get_trades('LEAGUE_ID')
# Find problematic trade and inspect pick data
"
```

2. **Regenerate after fixes:**
```bash
python src/update_index.py
```

3. **Verify in browser** that picks show ownership properly

## Success Criteria

✅ Picks show format: "TeamName's YYYY Round X pick"  
✅ Timeline data includes correct pick counts  
✅ Both HTML template and JavaScript data are consistent  
✅ Fallback logic handles missing ownership gracefully