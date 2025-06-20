#!/usr/bin/env python3
import re
import json
from datetime import datetime
import os

def extract_trade_data_from_service():
    """Generate fresh trade data and extract just the data portions"""
    
    print("🔄 Generating fresh trade data...")
    
    # Generate the latest trade visualization to a temporary file
    os.system('python src/regenerate_trade_visualization.py')
    
    # The regeneration creates trade_visualization_league_1181025001438806016_updated.html
    temp_file = 'trade_visualization_league_1181025001438806016_updated.html'
    
    if not os.path.exists(temp_file):
        print("❌ ERROR: Could not generate trade data")
        return None
    
    print("✅ Generated fresh trade data")
    
    # Read the temporary file and extract data
    with open(temp_file, 'r', encoding='utf-8') as f:
        temp_content = f.read()
    
    # Extract the data sections
    extracted_data = {}
    
    # 1. Network data
    network_match = re.search(r'const networkData = ({.*?});', temp_content, re.DOTALL)
    if network_match:
        extracted_data['networkData'] = network_match.group(1)
        print("✅ Extracted networkData")
    
    # 2. Timeline data  
    timeline_match = re.search(r'const timelineData = ({.*?});', temp_content, re.DOTALL)
    if timeline_match:
        extracted_data['timelineData'] = timeline_match.group(1)
        print("✅ Extracted timelineData")
    
    # 3. Most traded players
    players_match = re.search(r'const mostTradedPlayers = (\[.*?\]);', temp_content, re.DOTALL)
    if players_match:
        extracted_data['mostTradedPlayers'] = players_match.group(1)
        print("✅ Extracted mostTradedPlayers")
    
    # 4. Trade matrix
    matrix_match = re.search(r'const tradeMatrix = ({.*?});', temp_content, re.DOTALL)
    if matrix_match:
        extracted_data['tradeMatrix'] = matrix_match.group(1)
        print("✅ Extracted tradeMatrix")
    
    # Parse timeline data to verify June 2025 trades
    try:
        timeline_json = json.loads(extracted_data['timelineData'])
        june_trades = timeline_json.get('monthly_breakdown', {}).get('2025-06', 0)
        if june_trades > 0:
            print(f"✅ Verified: {june_trades} June 2025 trades found in fresh data")
        else:
            print("⚠️  Warning: No June 2025 trades found in fresh data")
    except:
        print("⚠️  Warning: Could not parse timeline data for verification")
    
    return extracted_data

def update_trade_data_only():
    """Update ONLY trade data while preserving ALL other functionality"""
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'index_backup_trade_update_{timestamp}.html'
    
    print("🔄 Starting surgical trade data update...")
    
    try:
        # Step 1: Backup
        with open('index.html', 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        print(f"✅ Backed up original to: {backup_path}")
        
        # Step 2: Extract fresh trade data
        fresh_data = extract_trade_data_from_service()
        if not fresh_data:
            print("❌ ERROR: Could not extract fresh trade data")
            return False
        
        # Step 3: Replace ONLY trade data in original content
        updated_content = original_content
        
        for data_name, new_data in fresh_data.items():
            if data_name == 'networkData':
                pattern = r'const networkData = ({.*?});'
            elif data_name == 'timelineData':
                pattern = r'const timelineData = ({.*?});'
            elif data_name == 'mostTradedPlayers':
                pattern = r'const mostTradedPlayers = (\[.*?\]);'
            elif data_name == 'tradeMatrix':
                pattern = r'const tradeMatrix = ({.*?});'
            else:
                continue
            
            old_match = re.search(pattern, updated_content, re.DOTALL)
            if old_match:
                # Replace old data with new data
                updated_content = updated_content.replace(
                    f'const {data_name} = {old_match.group(1)};',
                    f'const {data_name} = {new_data};'
                )
                print(f"✅ Updated {data_name}")
            else:
                print(f"⚠️  Warning: Could not find {data_name} in original file")
        
        # Step 4: Save updated content
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        # Step 5: Verify Firebase and June trades are both present
        firebase_check = 'firebase' in updated_content.lower()
        
        try:
            # Check for June 2025 in the updated content
            timeline_match = re.search(r'const timelineData = ({.*?});', updated_content, re.DOTALL)
            if timeline_match:
                timeline_json = json.loads(timeline_match.group(1))
                june_trades = timeline_json.get('monthly_breakdown', {}).get('2025-06', 0)
                june_check = june_trades > 0
            else:
                june_check = False
        except:
            june_check = False
        
        print(f"🔍 Verification:")
        print(f"   Firebase preserved: {'✅' if firebase_check else '❌'}")
        print(f"   June 2025 trades: {'✅' if june_check else '❌'} ({june_trades if june_check else 0} trades)")
        
        if firebase_check and june_check:
            print("🎉 Successfully updated trade data while preserving Firebase!")
            return True
        else:
            print("⚠️  Some functionality may be missing")
            return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        # Restore from backup
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open('index.html', 'w', encoding='utf-8') as f:
                f.write(backup_content)
            print("🔄 Restored from backup")
        except:
            pass
        return False

if __name__ == "__main__":
    success = update_trade_data_only()
    if success:
        print("\n🎉 Trade data update completed!")
        print("Your index.html now has the latest trades with Firebase functionality preserved.")
    else:
        print("\n❌ Update failed.")