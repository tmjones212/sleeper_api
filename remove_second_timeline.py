#!/usr/bin/env python3
"""
Remove the second timeline container
"""

def remove_second_timeline():
    # Read current index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the second timeline container
    timeline_count = 0
    second_timeline_line = -1
    
    for i, line in enumerate(lines):
        if '<div class="timeline-container">' in line:
            timeline_count += 1
            if timeline_count == 2:
                second_timeline_line = i
                break
    
    if second_timeline_line == -1:
        print("No second timeline container found")
        return
    
    print(f"Found second timeline container at line {second_timeline_line + 1}")
    
    # Find the closing div for this timeline
    div_count = 1
    end_line = second_timeline_line
    
    for i in range(second_timeline_line + 1, len(lines)):
        if '<div' in lines[i]:
            div_count += lines[i].count('<div')
        if '</div>' in lines[i]:
            div_count -= lines[i].count('</div>')
        
        if div_count == 0:
            end_line = i
            break
    
    print(f"Second timeline ends at line {end_line + 1}")
    
    # Remove lines from second timeline start to its end
    new_lines = lines[:second_timeline_line] + lines[end_line + 1:]
    
    # Write back
    with open('index.html', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ Removed second timeline container")
    
    # Verify
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    count = content.count('<div class="timeline-container">')
    print(f"✅ Now have {count} timeline container(s)")

if __name__ == "__main__":
    remove_second_timeline()