#!/usr/bin/env python3
import re

def analyze_div_balance(filename, start_line, end_line):
    """Analyze div tag balance in a specific section of HTML file."""
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Get the section we're interested in
    section_lines = lines[start_line-1:end_line]
    
    opening_count = 0
    closing_count = 0
    div_stack = []
    
    for i, line in enumerate(section_lines):
        line_num = start_line + i
        
        # Count opening divs (excluding self-closing)
        opening_divs = re.findall(r'<div(?:\s[^>]*)?>(?!</)', line)
        opening_count += len(opening_divs)
        
        # Count closing divs
        closing_divs = re.findall(r'</div>', line)
        closing_count += len(closing_divs)
        
        # Track balance
        for _ in opening_divs:
            div_stack.append(line_num)
        
        for _ in closing_divs:
            if div_stack:
                div_stack.pop()
            else:
                print(f"Extra closing div at line {line_num}: {line.strip()}")
    
    print(f"\nAnalysis of lines {start_line} to {end_line}:")
    print(f"Opening <div> tags: {opening_count}")
    print(f"Closing </div> tags: {closing_count}")
    print(f"Balance: {opening_count - closing_count}")
    
    if div_stack:
        print(f"\nUnclosed divs opened at lines: {div_stack[:10]}...")
    
    return opening_count, closing_count

# Analyze the matchups panel section
print("=== Matchups Panel Section ===")
analyze_div_balance('index.html', 10778, 14326)

# Also check a bit before and after
print("\n=== Extended Range (including before matchups panel) ===")
analyze_div_balance('index.html', 10770, 14330)