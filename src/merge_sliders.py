#!/usr/bin/env python3
import re

print("Merging slider functionality into updated trades HTML...")

# Read the backup (with sliders)
with open('../index_backup_20250619_165401.html', 'r', encoding='utf-8') as f:
    backup_html = f.read()

# Read the new HTML (with updated trades)
with open('../index_new.html', 'r', encoding='utf-8') as f:
    new_html = f.read()

# Extract slider-related CSS from backup
css_pattern = r'\.trade-grade-container\s*{[^}]+}.*?\.trade-grade-result\s*{[^}]+}'
slider_css_match = re.search(css_pattern, backup_html, re.DOTALL)

if slider_css_match:
    slider_css = slider_css_match.group(0)
    print("Found slider CSS")
    
    # Find where to insert CSS in new HTML (before closing </style>)
    style_close = new_html.rfind('</style>')
    if style_close != -1:
        # Add the slider CSS before </style>
        new_html = new_html[:style_close] + '\n\n        /* Trade Rating Sliders */\n        ' + slider_css + '\n\n' + new_html[style_close:]
        print("Added slider CSS")

# Extract JavaScript functions from backup
# Find the updateTradeGrade and related functions
js_start = backup_html.find('function updateTradeGrade(')
if js_start != -1:
    # Find the end of the JavaScript section (before </script>)
    js_end = backup_html.find('</script>', js_start)
    slider_js = backup_html[js_start:js_end]
    
    # Extract just the functions we need
    functions_to_extract = [
        'updateTradeGrade',
        'updateTradeGradeDisplay', 
        'saveTradeRating',
        'loadTradeRatings',
        'gradeToText',
        'updateLeagueSummary'
    ]
    
    extracted_js = []
    for func_name in functions_to_extract:
        func_pattern = rf'function {func_name}\([^{{]*\){{[^{{]*{{[^}}]*}}[^}}]*}}'
        func_match = re.search(func_pattern, slider_js, re.DOTALL)
        if func_match:
            extracted_js.append(func_match.group(0))
    
    # Also get the Firebase/database related code
    firebase_pattern = r'// Firebase configuration.*?// End real-time updates'
    firebase_match = re.search(firebase_pattern, backup_html, re.DOTALL)
    if firebase_match:
        extracted_js.insert(0, firebase_match.group(0))
    
    # Find where to insert JS in new HTML
    script_close = new_html.rfind('</script>')
    if script_close != -1:
        js_to_insert = '\n\n        // Trade Rating System\n        ' + '\n\n        '.join(extracted_js) + '\n\n'
        new_html = new_html[:script_close] + js_to_insert + new_html[script_close:]
        print("Added JavaScript functions")

# Now we need to modify the trade rendering to include sliders
# Find the renderTradeItem function in new HTML
render_func_pattern = r'function renderTradeItem\(trade, index\) {.*?return html;.*?}'
render_match = re.search(render_func_pattern, new_html, re.DOTALL)

if render_match:
    old_render = render_match.group(0)
    
    # Find where to insert the grade container
    # Look for the closing of trade-detail div
    insert_point = old_render.rfind('</div></div></div>`')
    if insert_point != -1:
        # Add the grade container HTML before the closing divs
        grade_html = '''
                <div class="trade-grade-container">
                    <div style="margin-bottom: 8px; color: #e0e0e0; font-weight: 600;">👤 Your Trade Grade:</div>
                    <input type="range" min="0" max="100" value="50" class="trade-grade-slider" 
                           id="trade-grade-${index}" onchange="updateTradeGrade(${index}, this.value)">
                    <div class="trade-grade-labels">
                        <span>${teams[0]} Won</span>
                        <span>Even</span>
                        <span>${teams[teams.length-1]} Won</span>
                    </div>
                    <div class="trade-grade-result" id="trade-result-${index}">
                        <span style="color: #999999;">Move slider to grade</span>
                    </div>
                </div>'''
        
        new_render = old_render[:insert_point] + grade_html + old_render[insert_point:]
        new_html = new_html.replace(old_render, new_render)
        print("Modified trade rendering to include sliders")

# Add the global variables needed
globals_to_add = '''
        // Global variables for trade ratings
        let isUserChangingSlider = false;
        let db = null;
        let auth = null;
        let userName = localStorage.getItem('fantasyUserName') || null;
        let userId = localStorage.getItem('fantasyUserId') || null;
        window.leagueAverageRatings = {};
'''

# Insert after the first <script> tag
first_script = new_html.find('<script>') + len('<script>')
new_html = new_html[:first_script] + '\n' + globals_to_add + '\n' + new_html[first_script:]

# Save the merged file
with open('../index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("\nSuccessfully merged sliders into index.html with updated trades!")
print("Your original is backed up as index_backup_20250619_165401.html")