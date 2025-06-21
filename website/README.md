# Eazy Pickens - Modular JavaScript Structure

This directory contains the modularized JavaScript code extracted from the original index.html file.

## Structure

```
website/
├── src/
│   ├── js/
│   │   ├── main.js                 # Main application entry point
│   │   └── modules/
│   │       ├── panels.js           # Panel switching functionality
│   │       ├── firebase.js         # Firebase initialization and operations
│   │       ├── charts.js           # Chart.js visualizations
│   │       ├── network.js          # Network graph visualization
│   │       ├── tradeHistory.js     # Trade history and grading
│   │       ├── matchups.js         # Matchup display and breakdowns
│   │       ├── draft.js            # Draft board functionality
│   │       ├── playerJourney.js    # Player journey tracking
│   │       ├── modal.js            # Modal management
│   │       ├── utils.js            # Utility functions
│   │       ├── externalData.js     # External data management
│   │       └── data/
│   │           ├── networkData.js  # Network visualization data
│   │           ├── timelineData.js # Timeline data
│   │           └── draftData.js    # Draft data structure
│   ├── styles/
│   │   └── css/
│   │       ├── main.css           # Main styles
│   │       └── components/        # Component-specific styles
│   └── data/                      # JSON data files
├── scripts/
│   └── extractData.js             # Script to extract data from index.html
├── index.html                     # Main HTML file
├── package.json                   # Node.js package configuration
└── README.md                      # This file
```

## Key Features Preserved

1. **Firebase Integration**: All Firebase code for real-time trade grading and synchronization
2. **Trade Network Visualization**: Interactive network graph showing trade relationships
3. **Trade History**: Complete trade timeline with grading functionality
4. **Matchup Breakdowns**: Player-by-player matchup analysis
5. **Draft Board**: Multi-year draft results visualization
6. **Player Journey**: Track players through trades
7. **Trade Matrix**: Team-to-team trade frequency

## Module Dependencies

- **panels.js**: Core panel switching functionality
- **firebase.js**: Handles all Firebase operations (critical - contains the Firebase config that was getting lost)
- **charts.js**: Monthly trade activity chart
- **network.js**: Trade network visualization using vis.js
- **tradeHistory.js**: Trade timeline, filtering, and grading
- **matchups.js**: Matchup display and player breakdowns
- **draft.js**: Draft board generation
- **playerJourney.js**: Player movement tracking
- **modal.js**: Modal creation and management
- **utils.js**: Common utility functions
- **externalData.js**: Manages data from external scripts (matchup_breakdowns.js, league_mapping.js)

## External Dependencies

The application relies on these external files:
- `matchup_breakdowns.js`: Player-level matchup data
- `league_mapping.js`: League ID to year mapping
- External libraries: Chart.js, vis.js, D3.js, Firebase

## Usage

1. Install dependencies: `npm install`
2. For development: `npm run dev`
3. For production build: `npm run build`

## Important Notes

- The Firebase configuration is preserved in `firebase.js` module
- All functionality from the original index.html has been preserved
- External data files (matchup_breakdowns.js, league_mapping.js) must be present
- The modular structure makes it easier to maintain and update specific features