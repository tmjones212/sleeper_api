#!/usr/bin/env python3
import re

# Read the current index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find and replace the problematic section in manualRefreshRatings
# The issue is that it's setting slider values for trades that don't have ratings

old_code = '''                    // Update individual sliders with THIS USER's ratings only (without saving)
                    Object.entries(userRatings).forEach(([tradeIndex, rating]) => {
                        const slider = document.getElementById(`trade-grade-${tradeIndex}`);
                        if (slider) {
                            if (!silent) console.log(`🎯 Setting slider ${tradeIndex} to user's rating: ${rating}`);
                            slider.value = rating;
                            // Update display only, don't save to Firebase to prevent infinite loop
                            updateTradeGradeDisplay(tradeIndex, rating, 1);
                        }
                    });'''

new_code = '''                    // Update individual sliders with THIS USER's ratings only (without saving)
                    // First, reset all sliders to default (50) if they don't have a user rating
                    document.querySelectorAll('.trade-grade-slider').forEach(slider => {
                        const tradeIndex = slider.id.replace('trade-grade-', '');
                        if (!userRatings.hasOwnProperty(tradeIndex)) {
                            // No rating from this user, set to default
                            slider.value = 50;
                            // Clear any previous display
                            const resultElement = document.getElementById(`trade-result-${tradeIndex}`);
                            if (resultElement) {
                                resultElement.innerHTML = '<span style="color: #999999;">Move slider to grade</span>';
                            }
                        }
                    });
                    
                    // Now update sliders that DO have user ratings
                    Object.entries(userRatings).forEach(([tradeIndex, rating]) => {
                        const slider = document.getElementById(`trade-grade-${tradeIndex}`);
                        if (slider) {
                            if (!silent) console.log(`🎯 Setting slider ${tradeIndex} to user's rating: ${rating}`);
                            slider.value = rating;
                            // Update display only, don't save to Firebase to prevent infinite loop
                            updateTradeGradeDisplay(tradeIndex, rating, 1);
                        }
                    });'''

# Replace the code
html_content = html_content.replace(old_code, new_code)

# Also fix the loadTradeGrades function to be called after page load
# Find where to add the call
window_onload_pattern = r'(window\.addEventListener\(\'load\', function\(\) \{[^}]+)'

# Check if loadTradeGrades() is already being called
if 'loadTradeGrades()' not in html_content:
    # Find the window.onload section and add loadTradeGrades call
    init_section = re.search(r'(// Initialize on page load\s*window\.addEventListener\(\'load\', function\(\) \{)', html_content)
    if init_section:
        insert_point = init_section.end()
        # Add loadTradeGrades call
        new_init = '''
            // Load user's saved ratings from localStorage first
            loadTradeGrades();
            '''
        html_content = html_content[:insert_point] + new_init + html_content[insert_point:]

# Write the fixed HTML back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ Fixed Firebase rating display issues")
print("✅ Sliders will now show:")
print("   - Your saved rating if you have one")
print("   - Default position (50) if you haven't rated yet")
print("   - Won't show random ratings from other users")