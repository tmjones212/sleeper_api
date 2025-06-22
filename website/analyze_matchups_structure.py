#!/usr/bin/env python3

def analyze_div_structure(filename, start_line, end_line):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    div_stack = []
    indent = 0
    
    for i in range(start_line - 1, min(end_line, len(lines))):
        line = lines[i].strip()
        line_num = i + 1
        
        if '<div' in line:
            # Extract id or class if present
            id_match = 'id="([^"]*)"' if 'id=' in line else ''
            class_match = 'class="([^"]*)"' if 'class=' in line else ''
            
            identifier = ''
            if id_match:
                import re
                match = re.search(r'id="([^"]*)"', line)
                if match:
                    identifier = f"#{match.group(1)}"
            elif class_match:
                import re
                match = re.search(r'class="([^"]*)"', line)
                if match:
                    identifier = f".{match.group(1).split()[0]}"
            
            div_stack.append((line_num, identifier, indent))
            print(f"{' ' * indent}Line {line_num}: <div {identifier}>")
            indent += 2
            
        elif '</div>' in line:
            if div_stack:
                start_line_num, identifier, start_indent = div_stack.pop()
                indent -= 2
                print(f"{' ' * indent}Line {line_num}: </div> (closes {identifier} from line {start_line_num})")
            else:
                print(f"Line {line_num}: </div> ⚠️  EXTRA CLOSING DIV")
    
    if div_stack:
        print("\n⚠️  UNCLOSED DIVS:")
        for line_num, identifier, _ in div_stack:
            print(f"  Line {line_num}: {identifier}")

# Analyze matchups panel structure
print("Analyzing matchups panel structure (lines 11089-14640):")
analyze_div_structure('dist/index.html', 11089, 14640)