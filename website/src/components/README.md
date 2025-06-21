# Fantasy Football Website Components

This directory contains modular HTML component templates for the fantasy football analytics website.

## Structure

```
components/
├── base.html                    # Base layout template
├── header.html                  # Site header
├── panels/                      # Main visualization panels
│   ├── overview.html           # Trade overview with statistics
│   ├── network.html            # Interactive trade network
│   ├── matrix.html             # Team-to-team trade matrix
│   ├── timeline.html           # Trade history timeline
│   ├── players.html            # Player journey tracker
│   ├── matchups.html           # Head-to-head matchups
│   └── draft.html              # Draft results
├── trades/                      # Trade-related components
│   ├── trade-item.html         # Individual trade display
│   ├── trade-summary.html      # Trading performance summary table
│   ├── trade-grade.html        # Trade grading slider
│   ├── player-card.html        # Player card for most traded
│   └── team-trader-card.html   # Team trading statistics card
├── shared/                      # Shared components
│   ├── controls.html           # Tab navigation controls
│   └── modals.html             # Modal dialogs
├── styles/                      # Modular CSS files
│   ├── network.css             # Network visualization styles
│   ├── matchups.css            # Matchup panel styles
│   ├── draft.css               # Draft board styles
│   ├── tables.css              # Table and matrix styles
│   ├── players.css             # Player journey styles
│   └── utilities.css           # Utility classes
├── scripts/                     # JavaScript modules
│   └── early-functions.js      # Functions needed early in page load
└── styles.css                   # Main stylesheet
```

## Template Variables

Templates use placeholder variables in the format `{{VARIABLE_NAME}}` that should be replaced with actual data:

### Base Template (`base.html`)
- `{{PAGE_TITLE}}` - Page title
- `{{STYLES}}` - Combined CSS imports
- `{{EARLY_SCRIPTS}}` - Scripts needed before page content
- `{{HEADER_COMPONENT}}` - Header HTML
- `{{CONTROLS_COMPONENT}}` - Navigation controls
- `{{OVERVIEW_PANEL}}` - Overview panel content
- `{{NETWORK_PANEL}}` - Network panel content
- `{{MATRIX_PANEL}}` - Matrix panel content
- `{{TIMELINE_PANEL}}` - Timeline panel content
- `{{PLAYERS_PANEL}}` - Players panel content
- `{{MATCHUPS_PANEL}}` - Matchups panel content
- `{{DRAFT_PANEL}}` - Draft panel content
- `{{MODALS}}` - Modal dialogs
- `{{SCRIPTS}}` - Main JavaScript code

### Header Component (`header.html`)
- `{{SITE_TITLE}}` - Main site title (e.g., "Eazy Pickens")
- `{{SITE_SUBTITLE}}` - Subtitle text

### Panel Components
Each panel has specific placeholders for dynamic content:
- Overview: `{{TOTAL_TRADES}}`, `{{TOTAL_PLAYERS_TRADED}}`, `{{TOTAL_PICKS_TRADED}}`, `{{ACTIVE_TEAMS}}`, `{{MOST_ACTIVE_TRADERS}}`, `{{MOST_TRADED_PLAYERS}}`
- Network: `{{TOTAL_TEAMS}}`, `{{TRADE_RELATIONSHIPS}}`
- Matrix: `{{TRADE_MATRIX_TABLE}}`
- Timeline: `{{TEAM_OPTIONS}}`, `{{TRADE_HISTORY}}`
- Players: Dynamic JavaScript-driven content
- Matchups: `{{MATCHUP_YEAR_OPTIONS}}`, `{{MATCHUP_DATA}}`
- Draft: `{{DRAFT_YEAR_OPTIONS}}`, `{{DRAFT_DATA}}`

### Trade Components
- Trade Item: `{{TRADE_DATE}}`, `{{TEAM1}}`, `{{TEAM2}}`, `{{PLAYERS_COUNT}}`, `{{PICKS_COUNT}}`, `{{TEAM1_RECEIVES}}`, `{{TEAM2_RECEIVES}}`, `{{TRADE_GRADE_SECTION}}`
- Trade Grade: `{{TRADE_ID}}`, `{{TEAM1}}`, `{{TEAM2}}`
- Player Card: `{{PLAYER_NAME}}`, `{{PLAYER_IMAGE_URL}}`, `{{TRADE_COUNT}}`
- Team Trader Card: `{{TEAM_NAME}}`, `{{TOTAL_TRADES}}`, `{{PLAYERS_ACQUIRED}}`, `{{PLAYERS_GIVEN}}`

## Usage

To build the website:

1. Load the base template
2. Replace all placeholder variables with actual data
3. Combine all CSS files into the `{{STYLES}}` section
4. Insert component HTML into their respective placeholders
5. Add JavaScript code to the `{{SCRIPTS}}` section

Example build process:
```python
# Load base template
with open('base.html', 'r') as f:
    html = f.read()

# Replace components
html = html.replace('{{HEADER_COMPONENT}}', header_html)
html = html.replace('{{CONTROLS_COMPONENT}}', controls_html)
# ... etc

# Replace data placeholders
html = html.replace('{{TOTAL_TRADES}}', str(total_trades))
# ... etc

# Save final HTML
with open('index.html', 'w') as f:
    f.write(html)
```

## Styling

The modular CSS files can be combined in this order:
1. `styles.css` - Main styles
2. `network.css` - Network-specific styles
3. `matchups.css` - Matchup panel styles
4. `draft.css` - Draft board styles
5. `tables.css` - Table and matrix styles
6. `players.css` - Player journey styles
7. `utilities.css` - Utility classes

## JavaScript Integration

The `early-functions.js` script should be included in the `<head>` section to ensure tab functionality works immediately when buttons are rendered.

Additional JavaScript for data visualization, Firebase integration, and interactive features should be added to the `{{SCRIPTS}}` section at the end of the document.