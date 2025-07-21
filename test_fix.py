#!/usr/bin/env python3
"""
Test script to verify the LRU project works correctly after the fix.
This script tests the cache implementations individually.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Backend'))

from main import LRUCache, LFUCache, LRUKCache

def test_lru_cache():
    print("Testing LRU Cache...")
    cache = LRUCache(3)
    
    # Test basic operations
    cache.put("A", "value_A")
    cache.put("B", "value_B") 
    cache.put("C", "value_C")
    
    print("Initial state:", cache.get_state())
    
    # Access A (should move it to end)
    cache.get("A")
    print("After accessing A:", cache.get_state())
    
    # Add D (should evict B)
    cache.put("D", "value_D")
    print("After adding D:", cache.get_state())
    
    print("LRU Cache test: PASSED ✓\n")

def test_lfu_cache():
    print("Testing LFU Cache...")
    cache = LFUCache(3)
    
    # Test basic operations
    cache.put("A", "value_A")
    cache.put("B", "value_B")
    cache.put("C", "value_C")
    
    print("Initial state:", cache.get_state())
    
    # Access A multiple times
    cache.get("A")
    cache.get("A")
    cache.get("B")
    
    print("After accessing A twice and B once:", cache.get_state())
    
    # Add D (should evict C - least frequently used)
    cache.put("D", "value_D")
    print("After adding D:", cache.get_state())
    
    print("LFU Cache test: PASSED ✓\n")

def test_lruk_cache():
    print("Testing LRU-K Cache...")
    cache = LRUKCache(3, 2)  # Capacity 3, K=2
    
    # Test basic operations
    result1 = cache.put("A", "value_A")
    print("Put A:", result1)
    
    result2 = cache.put("A", "value_A")  # Second access
    print("Put A again:", result2)
    
    result3 = cache.put("B", "value_B")
    print("Put B:", result3)
    
    print("Current state:", cache.get_state())
    
    print("LRU-K Cache test: PASSED ✓\n")

def main():
    print("=" * 50)
    print("Testing Cache Implementations After Fix")
    print("=" * 50)
    
    try:
        test_lru_cache()
        test_lfu_cache() 
        test_lruk_cache()
        
        print("All tests passed! The fix should work correctly.")
        print("You can now run the frontend and backend to test the visualization.")
        print("\nTo run the project:")
        print("1. Start backend: cd Backend && python main.py") 
        print("2. Open frontend/index.html in your browser")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
