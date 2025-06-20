#!/usr/bin/env python3
import re
import shutil
from datetime import datetime
import os

def safe_update_trades_preserve_firebase():
    """Safely update trades while preserving Firebase sliders, ratings, and ALL custom functionality"""
    
    # Create timestamp for backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'index_backup_firebase_{timestamp}.html'
    
    print("🔄 Starting safe trade update with Firebase preservation...")
    
    # Step 1: Backup current index.html
    try:
        shutil.copy('index.html', backup_path)
        print(f"✅ Backed up current index.html to: {os.path.basename(backup_path)}")
    except Exception as e:
        print(f"❌ ERROR: Could not create backup: {e}")
        return False
    
    # Step 2: Read current file with ALL functionality BEFORE generating new data
    print("🔄 Reading current file with Firebase, sliders, and ratings...")
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            original_html = f.read()
        print("✅ Saved current functionality")
    except Exception as e:
        print(f"❌ ERROR: Could not read current file: {e}")
        return False
    
    # Step 3: Generate new trade data (this will overwrite index.html)
    print("🔄 Generating new trade data...")
    try:
        os.system('python src/regenerate_trade_visualization.py')
        print("✅ Generated new trade data")
    except Exception as e:
        print(f"❌ ERROR: Could not generate new trade data: {e}")
        return False
    
    # Step 4: Preserve ALL custom functionality
    try:
        # Read the newly generated file (with updated trades but no custom functionality)
        with open('index.html', 'r', encoding='utf-8') as f:
            new_html = f.read()
        
        print("🔄 Preserving Firebase, sliders, ratings, and updating trade data...")
        
        # Strategy: Take the new trade data but preserve EVERYTHING else from original
        
        # Extract ONLY the trade data sections from new HTML
        data_to_update = {}
        
        # 1. Network data (trade relationships)
        network_match = re.search(r'const networkData = ({.*?});', new_html, re.DOTALL)
        if network_match:
            data_to_update['networkData'] = network_match.group(1)
            print("✅ Extracted new networkData")
        
        # 2. Timeline data (trade timeline)
        timeline_match = re.search(r'const timelineData = ({.*?});', new_html, re.DOTALL)
        if timeline_match:
            data_to_update['timelineData'] = timeline_match.group(1)
            print("✅ Extracted new timelineData")
        
        # 3. Most traded players
        players_match = re.search(r'const mostTradedPlayers = (\[.*?\]);', new_html, re.DOTALL)
        if players_match:
            data_to_update['mostTradedPlayers'] = players_match.group(1)
            print("✅ Extracted new mostTradedPlayers")
        
        # 4. Trade matrix
        matrix_match = re.search(r'const tradeMatrix = ({.*?});', new_html, re.DOTALL)
        if matrix_match:
            data_to_update['tradeMatrix'] = matrix_match.group(1)
            print("✅ Extracted new tradeMatrix")
        
        # Start with original HTML (has Firebase, sliders, ratings)
        updated_html = original_html
        
        # Replace ONLY the trade data sections
        for data_name, new_data in data_to_update.items():
            if data_name == 'networkData':
                pattern = r'const networkData = ({.*?});'
            elif data_name == 'timelineData':
                pattern = r'const timelineData = ({.*?});'
            elif data_name == 'mostTradedPlayers':
                pattern = r'const mostTradedPlayers = (\[.*?\]);'
            elif data_name == 'tradeMatrix':
                pattern = r'const tradeMatrix = ({.*?});'
            
            old_match = re.search(pattern, updated_html, re.DOTALL)
            if old_match:
                updated_html = updated_html.replace(old_match.group(1), new_data)
                print(f"✅ Updated {data_name} while preserving all other functionality")
            else:
                print(f"⚠️  Warning: Could not find {data_name} in original file")
        
        # Step 5: Save the updated file
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_html)
        
        print(f"✅ Successfully updated trades while preserving Firebase, sliders, and ratings!")
        print(f"📁 Original backed up as: {os.path.basename(backup_path)}")
        
        # Step 6: Verify Firebase is still there
        with open('index.html', 'r', encoding='utf-8') as f:
            verify_content = f.read()
        
        if 'firebase' in verify_content.lower() and 'trade-grade' in verify_content:
            print("✅ Verified: Firebase and slider functionality preserved")
        else:
            print("⚠️  Warning: Firebase or slider functionality may be missing")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        # Restore backup if something went wrong
        try:
            shutil.copy(backup_path, 'index.html')
            print(f"🔄 Restored from backup due to error")
        except:
            pass
        return False

if __name__ == "__main__":
    success = safe_update_trades_preserve_firebase()
    if success:
        print("\n🎉 Update completed successfully!")
        print("Your trade visualization now includes all the latest trades with Firebase sliders intact.")
    else:
        print("\n❌ Update failed. Your original file has been restored.")