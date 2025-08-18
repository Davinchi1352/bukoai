#!/usr/bin/env python3
"""
Python-based Drop Caps Test for Buko AI
This script properly handles Flask-WTF CSRF tokens and tests drop caps functionality
"""

import requests
import json
import re
from bs4 import BeautifulSoup
import sys

# Configuration
BASE_URL = "http://localhost:5001"
USER_EMAIL = "admin@buko-ai.com"
USER_PASSWORD = "admin123"
BOOK_ID = "33"
OUTPUT_DIR = "/tmp/drop_caps_test"

def extract_csrf_token(html_content):
    """Extract CSRF token from HTML form"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for hidden input with csrf_token name
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        return csrf_input.get('value')
    
    # Look for meta tag with csrf token
    csrf_meta = soup.find('meta', {'name': 'csrf-token'})
    if csrf_meta:
        return csrf_meta.get('content')
    
    # Look for csrf token in form data attributes
    form = soup.find('form')
    if form and form.get('data-csrf'):
        return form.get('data-csrf')
    
    return None

def test_drop_caps():
    """Test drop caps functionality"""
    session = requests.Session()
    
    print("🧪 Drop Caps Test for Buko AI")
    print("=" * 50)
    
    # Step 1: Get login page and extract CSRF token
    print("📄 Getting login page...")
    try:
        login_page = session.get(f"{BASE_URL}/auth/login")
        login_page.raise_for_status()
        print(f"✅ Login page loaded (status: {login_page.status_code})")
        
        # Extract CSRF token
        csrf_token = extract_csrf_token(login_page.text)
        if csrf_token:
            print(f"🔑 CSRF token extracted: {csrf_token[:20]}...")
        else:
            print("⚠️  No CSRF token found, attempting login without it...")
        
    except requests.RequestException as e:
        print(f"❌ Failed to get login page: {e}")
        return False
    
    # Step 2: Login
    print("🔐 Attempting login...")
    login_data = {
        'email': USER_EMAIL,
        'password': USER_PASSWORD,
        'remember_me': False
    }
    
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    try:
        login_response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
        
        # Check for successful login (302 redirect or 200 with success indicator)
        if login_response.status_code == 302:
            print(f"✅ Login successful (redirected)")
        elif login_response.status_code == 200:
            # Check if we're still on login page (failed) or dashboard (success)
            if "login" in login_response.url.lower() or "iniciar sesión" in login_response.text:
                print(f"❌ Login failed - still on login page")
                print("Response preview:", login_response.text[:500])
                return False
            else:
                print(f"✅ Login successful (status 200)")
        else:
            print(f"❌ Login failed (status: {login_response.status_code})")
            print("Response preview:", login_response.text[:500])
            return False
            
    except requests.RequestException as e:
        print(f"❌ Login request failed: {e}")
        return False
    
    # Step 3: Access formatting viewer
    print("👀 Accessing formatting viewer...")
    try:
        viewer_response = session.get(f"{BASE_URL}/books/book/{BOOK_ID}/formatting-viewer")
        viewer_response.raise_for_status()
        print(f"✅ Formatting viewer accessible (status: {viewer_response.status_code})")
        
        # Check if we're redirected to login (authentication failed)
        if "login" in viewer_response.url:
            print("❌ Redirected to login - authentication failed")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Failed to access formatting viewer: {e}")
        return False
    
    # Step 4: Test formatting preview with drop caps ENABLED
    print("🎨 Testing DROP CAPS ENABLED...")
    
    enabled_data = {
        "use_drop_caps": True,
        "font_family": "Crimson Pro",
        "font_size_body": 12,
        "line_spacing": 1.5,
        "include_title_page": True,
        "include_copyright_page": True,
        "include_table_of_contents": True,
        "author_name": "Test Author",
        "use_professional_typography": True,
        "use_chapter_breaks": True
    }
    
    try:
        enabled_response = session.post(
            f"{BASE_URL}/books/book/{BOOK_ID}/formatting-preview",
            json=enabled_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if enabled_response.status_code == 200:
            print(f"✅ Drop caps enabled request successful")
            enabled_json = enabled_response.json()
            
            # Save response
            with open(f"{OUTPUT_DIR}/drop_caps_enabled_response.json", 'w') as f:
                json.dump(enabled_json, f, indent=2)
                
        else:
            print(f"❌ Drop caps enabled request failed (status: {enabled_response.status_code})")
            print("Response:", enabled_response.text[:500])
            return False
            
    except requests.RequestException as e:
        print(f"❌ Drop caps enabled request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response for drop caps enabled: {e}")
        return False
    
    # Step 5: Test formatting preview with drop caps DISABLED
    print("🎨 Testing DROP CAPS DISABLED...")
    
    disabled_data = enabled_data.copy()
    disabled_data["use_drop_caps"] = False
    
    try:
        disabled_response = session.post(
            f"{BASE_URL}/books/book/{BOOK_ID}/formatting-preview",
            json=disabled_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if disabled_response.status_code == 200:
            print(f"✅ Drop caps disabled request successful")
            disabled_json = disabled_response.json()
            
            # Save response
            with open(f"{OUTPUT_DIR}/drop_caps_disabled_response.json", 'w') as f:
                json.dump(disabled_json, f, indent=2)
                
        else:
            print(f"❌ Drop caps disabled request failed (status: {disabled_response.status_code})")
            print("Response:", disabled_response.text[:500])
            return False
            
    except requests.RequestException as e:
        print(f"❌ Drop caps disabled request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response for drop caps disabled: {e}")
        return False
    
    # Step 6: Analyze responses
    print("🔍 Analyzing drop caps implementation...")
    
    def analyze_response(data, label):
        """Analyze a formatting response for drop caps patterns"""
        if 'preview_html' not in data:
            print(f"   {label}: No preview_html found")
            print(f"   Available keys: {list(data.keys())}")
            return None
        
        html = data['preview_html']
        
        # Count drop caps patterns
        drop_cap_letter_count = html.count('drop-cap-letter')
        data_drop_cap_count = html.count('data-drop-cap')
        data_drop_cap_char_count = html.count('data-drop-cap-char')
        
        print(f"   {label}:")
        print(f"     - HTML length: {len(html):,} characters")
        print(f"     - 'drop-cap-letter' class: {drop_cap_letter_count} occurrences")
        print(f"     - 'data-drop-cap' attribute: {data_drop_cap_count} occurrences")
        print(f"     - 'data-drop-cap-char' attribute: {data_drop_cap_char_count} occurrences")
        
        # Extract sample drop cap HTML if found
        if drop_cap_letter_count > 0:
            drop_cap_samples = re.findall(r'<span class="drop-cap-letter"[^>]*>[^<]*</span>', html)
            if drop_cap_samples:
                print(f"     - Sample drop cap HTML: {drop_cap_samples[0]}")
        
        return {
            'html_length': len(html),
            'drop_cap_letter': drop_cap_letter_count,
            'data_drop_cap': data_drop_cap_count,
            'data_drop_cap_char': data_drop_cap_char_count,
            'html': html
        }
    
    enabled_stats = analyze_response(enabled_json, "DROP CAPS ENABLED")
    disabled_stats = analyze_response(disabled_json, "DROP CAPS DISABLED")
    
    if not enabled_stats or not disabled_stats:
        print("❌ Cannot analyze - missing HTML data")
        return False
    
    # Step 7: Compare and conclude
    print("\n📊 COMPARISON RESULTS:")
    html_size_diff = enabled_stats['html_length'] - disabled_stats['html_length']
    print(f"   - HTML size difference: {html_size_diff:,} characters")
    
    # Check if drop caps features are properly implemented
    enabled_has_drop_caps = (enabled_stats['drop_cap_letter'] > 0 or 
                            enabled_stats['data_drop_cap'] > 0)
    
    disabled_has_drop_caps = (disabled_stats['drop_cap_letter'] > 0 or 
                             disabled_stats['data_drop_cap'] > 0)
    
    print(f"   - Drop caps in ENABLED response: {'✅ Found' if enabled_has_drop_caps else '❌ Not found'}")
    print(f"   - Drop caps in DISABLED response: {'❌ Found (unexpected)' if disabled_has_drop_caps else '✅ Not found (correct)'}")
    
    # Final verdict
    if enabled_has_drop_caps and not disabled_has_drop_caps:
        print(f"\n🎉 SUCCESS: Drop caps functionality is working correctly!")
        print(f"   ✅ Drop caps appear when enabled")
        print(f"   ✅ Drop caps are absent when disabled")
        
        # Save HTML samples
        with open(f"{OUTPUT_DIR}/drop_caps_enabled.html", 'w') as f:
            f.write(enabled_stats['html'])
        with open(f"{OUTPUT_DIR}/drop_caps_disabled.html", 'w') as f:
            f.write(disabled_stats['html'])
            
        print(f"\n📁 Files saved to: {OUTPUT_DIR}")
        return True
        
    else:
        print(f"\n❌ FAILURE: Drop caps functionality is not working correctly")
        if not enabled_has_drop_caps:
            print(f"   ❌ Drop caps not found in ENABLED response")
        if disabled_has_drop_caps:
            print(f"   ❌ Drop caps unexpectedly found in DISABLED response")
        return False

if __name__ == "__main__":
    # Create output directory
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    success = test_drop_caps()
    sys.exit(0 if success else 1)