# CSS Organization

The CSS has been extracted from index.html and organized into the following structure:

## Main CSS File
- `css/main.css` - Contains all core styles including base resets, layout, navigation, and utility classes

## Component CSS Files
Located in `css/components/`:
- `draft-board.css` - Styles for the draft board visualization
- `matchups.css` - Styles for matchup displays and results
- `modals.css` - Modal dialog styles
- `network.css` - Network visualization specific styles
- `player-journey.css` - Player journey and trading history styles
- `trade-components.css` - All trade-related component styles including tables, filters, and grading

## Usage in HTML

Replace the `<style>` tag in index.html with these link tags in the `<head>` section:

```html
<!-- Main CSS -->
<link rel="stylesheet" href="css/main.css">

<!-- Component CSS -->
<link rel="stylesheet" href="css/components/trade-components.css">
<link rel="stylesheet" href="css/components/draft-board.css">
<link rel="stylesheet" href="css/components/player-journey.css">
<link rel="stylesheet" href="css/components/network.css">
<link rel="stylesheet" href="css/components/matchups.css">
<link rel="stylesheet" href="css/components/modals.css">
```

## CSS Structure

### main.css sections:
1. Reset & Base Styles
2. Layout & Containers  
3. Header Styles
4. Controls & Navigation
5. Panels & Visualization Containers
6. Statistics & Cards
7. Network Visualization (base)
8. Trade Components (base)
9. Tables
10. Timeline
11. Player Journey (base)
12. Lists
13. Search & Inputs
14. Charts
15. Modals (base)
16. Draft Board (base)
17. Matchup Styles (base)
18. Utility Classes
19. Responsive Design

### Component files contain:
- Component-specific detailed styles
- Component-specific responsive adjustments
- Component-specific animations and transitions

## Benefits of this organization:
1. **Modularity** - Each component's styles are isolated
2. **Maintainability** - Easier to find and update specific styles
3. **Performance** - Can load only needed CSS for specific pages
4. **Reusability** - Components can be reused in other projects
5. **Team collaboration** - Multiple developers can work on different components without conflicts