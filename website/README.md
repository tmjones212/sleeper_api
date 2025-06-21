# Modular Fantasy Football Website

A maintainable, component-based architecture for your fantasy football league website.

## Overview

This new structure solves the problems with the monolithic index.html by:
- **Separating concerns**: HTML, CSS, and JavaScript are in separate files
- **Component-based**: Each feature is its own module that can be updated independently
- **Preserves custom code**: Firebase integration and trade sliders are protected
- **Easy updates**: Update specific sections without touching others
- **Build process**: Combines components into optimized output

## Directory Structure

```
website/
├── src/                    # Source files
│   ├── components/         # HTML templates
│   │   ├── panels/        # Main content panels
│   │   ├── trades/        # Trade-related components
│   │   └── shared/        # Shared components
│   ├── js/                # JavaScript modules
│   │   └── modules/       # Feature modules
│   ├── styles/            # CSS files
│   │   └── css/          # Component styles
│   └── data/             # JSON data files
├── build/                 # Build scripts
│   ├── site_generator.py  # Main build script
│   └── component_updater.py # Component update system
├── update_scripts/        # Section-specific updaters
│   ├── update_trades.py   # Trade data updater
│   ├── update_network.py  # Network viz updater
│   └── update_matchups.py # Matchup data updater
├── dist/                  # Generated output
│   └── index.html        # Built website
├── Makefile              # Build commands
├── build.sh              # Shell build script
└── README.md             # This file
```

## Quick Start

### 1. Build the Complete Website
```bash
# Using Make
make build

# Using shell script
./build.sh build

# Using Python directly
python3 build/site_generator.py --build
```

### 2. Update Specific Sections
```bash
# Update only trades (preserves Firebase and grades)
make update-trades LEAGUE=1181025001438806016

# Update network visualization
make update-network

# Update matchups
make update-matchups

# Update everything
make update-all
```

### 3. Development Server
```bash
# Start local server at http://localhost:8000
make dev
# or
./build.sh dev
```

### 4. Deploy
```bash
# Copy to parent directory
make deploy
# or
./build.sh deploy
```

## Key Features

### 1. Protected Sections
The system preserves these critical sections during updates:
- **Firebase Configuration**: Won't lose Firebase integration
- **Trade Rating Sliders**: User grades are preserved
- **Custom Functions**: Any custom code you add

### 2. Component-Based Updates
Update individual components without regenerating the entire site:
```python
# Update just the trade section
python3 update_scripts/update_trades.py --league YOUR_LEAGUE_ID

# The script will:
# 1. Fetch fresh trade data
# 2. Preserve existing trade grades
# 3. Update only the trade section
# 4. Keep Firebase code intact
```

### 3. Modular JavaScript
JavaScript is organized into modules:
- `firebase.js` - Firebase integration (finally safe!)
- `panels.js` - Panel switching logic
- `tradeHistory.js` - Trade display and filtering
- `network.js` - Network visualization
- `charts.js` - Chart.js integrations
- `matchups.js` - Matchup displays
- `draft.js` - Draft board
- `playerJourney.js` - Player tracking

### 4. Organized CSS
Styles are split into logical files:
- `main.css` - Core styles
- `components/trade-components.css` - Trade-specific styles
- `components/draft-board.css` - Draft board styles
- `components/network.css` - Network visualization
- etc.

## Common Tasks

### Adding a New Protected Section
```python
# In your Python script
from component_updater import ComponentUpdater

updater = ComponentUpdater()
updater.add_protected_section('my_custom_code', '''
<script>
// Your custom code here
function myCustomFunction() {
    console.log("This won't be lost!");
}
</script>
''')
```

### Updating After League Activity
```bash
# Quick update after new trades
make update-trades

# Full refresh of all data
make update-all

# Deploy to production
make deploy
```

### Customizing Components
1. Edit the template in `src/components/`
2. Rebuild: `make build`
3. Your changes are now in the generated site

## Migration from Old System

### Initial Setup
1. Run `make build` to generate the new index.html
2. Copy any custom code from your old index.html
3. Add it as a protected section
4. Test thoroughly

### Preserving Existing Data
The system automatically:
- Extracts and preserves trade grades
- Maintains Firebase configuration
- Keeps custom functions intact

## Advantages Over Monolithic index.html

1. **Easy to Edit**: Each component is a small, focused file
2. **Safe Updates**: Can't accidentally delete Firebase code
3. **Version Control**: See exactly what changed in each component
4. **Parallel Development**: Multiple features can be updated independently
5. **Testing**: Can test individual components
6. **Performance**: Only update what changed
7. **Debugging**: Errors are isolated to specific modules

## Troubleshooting

### Firebase Code Missing
The Firebase code is now in `src/js/modules/firebase.js` and protected by markers. It won't disappear anymore!

### Trade Grades Lost
Use `make update-trades` which automatically preserves grades. Use `--no-preserve-grades` flag only if you want to reset them.

### Build Errors
Check that all paths in `build/site_generator.py` are correct and all dependencies are installed.

## Future Enhancements

This modular structure enables:
- React/Vue migration (components are ready)
- API integration (modules can fetch data directly)
- Real-time updates (WebSocket support)
- Multiple themes (swap CSS files)
- A/B testing (serve different components)
- Performance optimization (lazy loading)

## Contributing

When adding new features:
1. Create a new component in `src/components/`
2. Add corresponding JavaScript module
3. Update the build script to include it
4. Add an update script if it has dynamic data
5. Document the feature

The modular structure makes it easy to add features without breaking existing functionality!