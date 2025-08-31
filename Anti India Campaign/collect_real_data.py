"""
Quick Data Collection Script
Run this to populate database with real anti-India campaign data
"""

import time
import sys
import os
sys.path.append(os.path.dirname(__file__))

from enhanced_data_collector import EnhancedDataCollector
from database import init_database
from config import GOOGLE_DORKS, ANTI_INDIA_KEYWORDS

def collect_real_data():
    """Collect real data from various sources"""
    print("🚀 Starting Real Data Collection...")
    print("🗄️ Initializing database...")
    
    # Initialize database
    init_database()
    
    # Initialize collector
    collector = EnhancedDataCollector()
    
    # Ensure database is ready
    collector.ensure_database()
    
    total_collected = 0
    
    print(f"\n🔍 Using {len(GOOGLE_DORKS)} Google Dork patterns...")
    print("📊 Collecting from first 10 dorks for quick start...\n")
    
    # Use first 10 dorks for quick collection
    for i, dork in enumerate(GOOGLE_DORKS[:10], 1):
        print(f"🔍 [{i}/10] Searching: {dork}")
        
        try:
            # Search with rate limiting
            results = collector.google_dork_search(dork, max_results=5)
            
            if results:
                total_collected += len(results)
                print(f"   ✅ Found {len(results)} results")
            else:
                print(f"   ⚠️ No results found")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Rate limiting - be respectful to search engines
        print(f"   ⏳ Waiting 3 seconds...")
        time.sleep(3)
    
    print(f"\n✅ Collection Complete!")
    print(f"📊 Total articles collected: {total_collected}")
    print(f"🗄️ Data saved to: campaign_data.db")
    print(f"🌐 View in dashboard: http://localhost:8511")
    
    if total_collected > 0:
        print(f"\n🎉 Success! Your dashboard now has real data.")
        print(f"🔄 Refresh your browser to see the results.")
    else:
        print(f"\n⚠️ No data collected. This might be due to:")
        print(f"   • Rate limiting by search engines")
        print(f"   • Network connectivity issues")
        print(f"   • Need for API keys in config.py")

if __name__ == "__main__":
    collect_real_data()
