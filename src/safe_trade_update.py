#!/usr/bin/env python3
import re
import shutil
from datetime import datetime
import os

def safe_update_trades():
    """Safely update trades while preserving sliders and all customizations"""
    
    # Create timestamp for backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'../index_backup_{timestamp}.html'
    
    print("🔄 Starting safe trade update process...")
    
    # Step 1: Backup current index.html
    try:
        shutil.copy('index.html', backup_path)
        print(f"✅ Backed up current index.html to: {os.path.basename(backup_path)}")
    except Exception as e:
        print(f"❌ ERROR: Could not create backup: {e}")
        return False
    
    # Step 2: Read current file with sliders BEFORE generating new data
    print("🔄 Reading current file with sliders...")
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_with_sliders = f.read()
        print("✅ Saved current slider settings")
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
    
    # Step 4: Preserve sliders and custom settings
    try:
        # Read the newly generated file (with updated trades but no sliders)
        with open('index.html', 'r', encoding='utf-8') as f:
            html_with_new_trades = f.read()
        
        print("🔄 Preserving sliders and updating trade data...")
        
        # Extract trade data from NEW file and sliders from OLD file
        # We want to use the NEW trade data but preserve the OLD sliders
        
        # Extract slider values from the backup (old file)
        slider_pattern = r'(\w+Slider\.value\s*=\s*[^;]+;)'
        old_sliders = re.findall(slider_pattern, html_with_sliders)
        
        # Start with the new HTML (has updated trades)
        updated_html = html_with_new_trades
        
        # Find where sliders are initialized in the new HTML and replace with old values
        if old_sliders:
            print(f"🔄 Restoring {len(old_sliders)} slider settings...")
            for old_slider in old_sliders:
                # Extract slider name and value
                slider_match = re.match(r'(\w+Slider)\.value\s*=\s*([^;]+);', old_slider)
                if slider_match:
                    slider_name = slider_match.group(1)
                    old_value = slider_match.group(2)
                    
                    # Replace the slider value in new HTML
                    new_slider_pattern = f'{slider_name}\\.value\\s*=\\s*[^;]+;'
                    replacement = f'{slider_name}.value = {old_value};'
                    updated_html = re.sub(new_slider_pattern, replacement, updated_html)
                    print(f"✅ Restored {slider_name}")
        else:
            print("⚠️  No sliders found to restore")
        
        # Step 5: Save the updated file
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_html)
        
        print(f"✅ Successfully updated trades while preserving sliders!")
        print(f"📁 Original backed up as: {os.path.basename(backup_path)}")
        
        # Step 6: Cleanup - no temporary files to clean up
        print("🧹 Process completed")
        
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
    success = safe_update_trades()
    if success:
        print("\n🎉 Update completed successfully!")
        print("Your trade visualization now includes all the latest trades.")
    else:
        print("\n❌ Update failed. Your original file is safe.")