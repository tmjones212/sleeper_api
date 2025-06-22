#!/usr/bin/env python3
import re

# Read the file
with open('dist/index.html', 'r') as f:
    content = f.read()

# Find matchups-panel
matchups_start = content.find('<div class="visualization-panel" id="matchups-panel">')
if matchups_start == -1:
    print("❌ ERROR: matchups-panel not found!")
    exit(1)

# Find panel-content inside matchups
panel_content_start = content.find('<div class="panel-content">', matchups_start)
if panel_content_start == -1 or panel_content_start > matchups_start + 5000:
    print("❌ ERROR: panel-content not found inside matchups-panel!")
    exit(1)

# Find matchupsContainer
container_start = content.find('<div id="matchupsContainer"', panel_content_start)
if container_start == -1:
    print("❌ ERROR: matchupsContainer not found!")
    exit(1)

# Check if matchupsContainer is after panel-content
if container_start < panel_content_start:
    print("❌ ERROR: matchupsContainer is before panel-content!")
    exit(1)

# Find closing tags
panel_close = content.find('</div> <!-- panel-content -->', container_start)
matchups_close = content.find('</div> <!-- matchups-panel -->', panel_close if panel_close != -1 else container_start)

print("✅ Structure looks correct!")
print(f"   matchups-panel at: line {content[:matchups_start].count(chr(10)) + 1}")
print(f"   panel-content at: line {content[:panel_content_start].count(chr(10)) + 1}")
print(f"   matchupsContainer at: line {content[:container_start].count(chr(10)) + 1}")
if panel_close != -1:
    print(f"   panel-content closes at: line {content[:panel_close].count(chr(10)) + 1}")
if matchups_close != -1:
    print(f"   matchups-panel closes at: line {content[:matchups_close].count(chr(10)) + 1}")

# Additional check - make sure container is between panel-content start and close
if panel_close != -1 and container_start > panel_close:
    print("❌ ERROR: matchupsContainer is after panel-content close!")
else:
    print("✅ matchupsContainer is properly inside panel-content!")