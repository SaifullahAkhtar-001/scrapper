#!/usr/bin/env python3
"""
Script to add test keywords to the database
This script adds some test keywords for the Todocoleccion scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.supabase_client import supabase_client

def add_test_keywords():
    """Add test keywords to the database"""
    print("=== Adding Test Keywords ===")
    
    # Test keywords for Todocoleccion scraper
    test_keywords = [
        "cigarro antiguo",
        "vintage cigar",
        "antique tobacco",
        "cigarro vintage",
        "cigar cutter vintage"
    ]
    
    try:
        for keyword in test_keywords:
            # Check if keyword already exists
            existing = supabase_client.client.table('keywords').select('*').eq('keyword', keyword).execute()
            
            if existing.data:
                print(f"⚠️  Keyword '{keyword}' already exists")
                continue
            
            # Add new keyword
            keyword_data = {
                'keyword': keyword,
                'is_active': True
            }
            
            result = supabase_client.client.table('keywords').insert(keyword_data).execute()
            
            if result.data:
                print(f"✅ Added keyword: '{keyword}'")
            else:
                print(f"❌ Failed to add keyword: '{keyword}'")
                
    except Exception as e:
        print(f"❌ Error adding keywords: {e}")

def list_keywords():
    """List all keywords in the database"""
    print("\n=== Current Keywords ===")
    
    try:
        keywords = supabase_client.get_all_keywords()
        
        if keywords:
            print(f"Found {len(keywords)} active keywords:")
            for i, kw in enumerate(keywords, 1):
                print(f"  {i}. {kw['keyword']}")
        else:
            print("No keywords found in database")
            
    except Exception as e:
        print(f"❌ Error listing keywords: {e}")

def main():
    """Main function"""
    print("Test Keywords Management")
    print("=" * 50)
    
    # Add test keywords
    add_test_keywords()
    
    # List current keywords
    list_keywords()
    
    print("\n" + "=" * 50)
    print("Keywords setup completed!")

if __name__ == "__main__":
    main() 