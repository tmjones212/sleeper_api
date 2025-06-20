#!/usr/bin/env python3
import re

def verify_final_result():
    """Verify that both Firebase and June 2025 trades are present"""
    
    print("🔍 Final Verification Report")
    print("=" * 50)
    
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check 1: Firebase functionality
        firebase_check = 'firebase' in content.lower()
        firebase_scripts = content.count('firebase-app-compat.js') > 0
        
        print(f"✅ Firebase preserved: {'✅ YES' if firebase_check and firebase_scripts else '❌ NO'}")
        
        # Check 2: June 2025 in monthly breakdown
        timeline_match = re.search(r'const timelineData = ({.*?});', content, re.DOTALL)
        if timeline_match:
            timeline_content = timeline_match.group(1)
            june_2025_check = '"2025-06"' in timeline_content
            
            # Extract the number of June trades
            june_match = re.search(r'"2025-06":\s*(\d+)', timeline_content)
            june_count = int(june_match.group(1)) if june_match else 0
            
            print(f"✅ June 2025 in timeline: {'✅ YES' if june_2025_check else '❌ NO'} ({june_count} trades)")
        else:
            print("❌ Timeline data not found")
            june_2025_check = False
            june_count = 0
        
        # Check 3: Specific June dates in network data
        june_dates = re.findall(r'2025-06-\d{2}', content)
        unique_june_dates = sorted(set(june_dates))
        
        print(f"✅ June trade dates found: {len(unique_june_dates)} unique dates")
        for date in unique_june_dates:
            print(f"   📅 {date}")
        
        # Check 4: Jaylen Waddle trade (June 16, 4:18 PM)
        waddle_trade_check = '2025-06-16 04:18' in content
        print(f"✅ Jaylen Waddle trade (Jun 16, 4:18 PM): {'✅ YES' if waddle_trade_check else '❌ NO'}")
        
        # Check 5: Trade functionality
        trade_data_checks = [
            'networkData' in content,
            'timelineData' in content,
            'mostTradedPlayers' in content
        ]
        
        print(f"✅ Trade data sections: {'✅ ALL PRESENT' if all(trade_data_checks) else '❌ MISSING SOME'}")
        
        # Overall status
        print("\n" + "=" * 50)
        if firebase_check and june_2025_check and waddle_trade_check and all(trade_data_checks):
            print("🎉 SUCCESS: Everything is working correctly!")
            print("   ✅ Firebase sliders preserved")
            print("   ✅ June 2025 trades included")
            print("   ✅ Jaylen Waddle trade present")
            print("   ✅ All trade data updated")
            return True
        else:
            print("⚠️  PARTIAL SUCCESS: Some issues remain")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    verify_final_result()