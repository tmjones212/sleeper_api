#!/bin/bash

# Get the last 30 commits
echo "Extracting index.html from the last 30 commits..."

# Counter for file naming
counter=1

# Get list of commits
git log --oneline -n 30 | while read -r line; do
    commit_hash=$(echo "$line" | awk '{print $1}')
    commit_message=$(echo "$line" | cut -d' ' -f2-)
    
    # Check if index.html exists in this commit
    if git show "${commit_hash}:index.html" &>/dev/null; then
        # Save the file with commit info in filename
        filename="index_html_versions/${counter}_${commit_hash}_index.html"
        
        echo "Saving commit ${commit_hash}: ${commit_message}"
        git show "${commit_hash}:index.html" > "$filename"
        
        # Create a companion info file
        echo "Commit: ${commit_hash}" > "${filename}.info"
        echo "Message: ${commit_message}" >> "${filename}.info"
        echo "Date: $(git show -s --format=%ci ${commit_hash})" >> "${filename}.info"
        
        ((counter++))
    else
        echo "No index.html in commit ${commit_hash}: ${commit_message}"
    fi
done

echo "Done! Extracted $((counter-1)) versions of index.html"