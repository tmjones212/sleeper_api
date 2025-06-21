#!/usr/bin/env python3

def trace_div_structure(filename):
    """Trace the div structure to understand proper nesting."""
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Start from line 14317 (last matchup card closes) and work backwards
    # Expected structure working backwards from the 8 closing divs:
    
    print("Expected structure for 8 closing divs at end of matchups panel:")
    print("Line 14317: </div> - closes team winner div (line 14313)")
    print("Line 14318: </div> - closes matchup-card div (line 14307)")  
    print("Line 14319: </div> - closes week-card div")
    print("Line 14320: </div> - closes weeks-container div")
    print("Line 14321: </div> - closes year-matchups div")
    print("Line 14322: </div> - closes matchupsContainer div")
    print("Line 14323: </div> - closes panel-content div")
    print("Line 14324: </div> - closes visualization-panel div")
    print("Line 14325: </div> - EXTRA! This is the problematic extra closing div")
    
    print("\n\nLet's verify the actual structure...")
    
    # Find key structural elements
    for i, line in enumerate(lines[10778:14326], start=10778):
        if 'id="matchups-panel"' in line:
            print(f"\nLine {i}: Opening matchups-panel")
        elif 'class="panel-content"' in line and i > 10778 and i < 14326:
            print(f"Line {i}: Opening panel-content")
        elif 'id="matchupsContainer"' in line:
            print(f"Line {i}: Opening matchupsContainer")
            
trace_div_structure('index.html')