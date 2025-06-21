#!/usr/bin/env python3
"""
Removes redundant trade summary text from index.html.
This includes the team names with ↔ symbol and player/pick counts.
"""
import re

def remove_trade_summaries(html_content):
    """Remove redundant trade summary information."""
    
    # Pattern to match the entire trade-summary div
    # This will match both empty summaries and ones with team names
    pattern = r'<div class="trade-summary">\s*<strong>[^<]*</strong>\s*<span[^>]*>[^<]*</span>\s*</div>'
    
    # Remove all trade summary divs
    updated_html = re.sub(pattern, '', html_content, flags=re.DOTALL)
    
    # Count how many were removed
    original_count = len(re.findall(r'<div class="trade-summary">', html_content))
    remaining_count = len(re.findall(r'<div class="trade-summary">', updated_html))
    removed_count = original_count - remaining_count
    
    print(f"Removed {removed_count} trade summary sections")
    
    return updated_html

def main():
    print("Removing redundant trade summaries from index.html...")
    
    # Read existing index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Remove trade summaries
    updated_html = remove_trade_summaries(html_content)
    
    # Write back to index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print("Successfully removed redundant trade summaries!")
    print("Trade history now shows only the date and team details without duplicate information.")

if __name__ == "__main__":
    main()