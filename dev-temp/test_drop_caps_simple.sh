#!/bin/bash

# Simplified Drop Caps Testing Script for Buko AI
set -e

# Configuration
BASE_URL="http://localhost:5001"
USER_EMAIL="admin@buko-ai.com"
USER_PASSWORD="admin123"
BOOK_ID="33"
COOKIE_JAR="/tmp/buko_cookies.txt"
OUTPUT_DIR="/tmp/drop_caps_test"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}=== Drop Caps Test - Simplified ===${NC}"
echo -e "${YELLOW}Base URL: $BASE_URL${NC}"
echo -e "${YELLOW}User: $USER_EMAIL${NC}"
echo -e "${YELLOW}Book ID: $BOOK_ID${NC}"

# Step 1: Try direct login (some Flask apps don't require CSRF for basic auth)
echo -e "\n${BLUE}--- Attempting Login ---${NC}"
login_response=$(curl -s -c "$COOKIE_JAR" \
    -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "email=$USER_EMAIL&password=$USER_PASSWORD" \
    -w "\n---HTTP_CODE---%{http_code}" \
    "$BASE_URL/auth/login")

login_code=$(echo "$login_response" | grep "---HTTP_CODE---" | sed 's/---HTTP_CODE---//')
login_body=$(echo "$login_response" | sed '/---HTTP_CODE---/d')

if [ "$login_code" -eq 302 ] || [ "$login_code" -eq 200 ]; then
    echo -e "${GREEN}✓ Login successful (HTTP $login_code)${NC}"
    
    # Step 2: Try to access formatting viewer
    echo -e "\n${BLUE}--- Testing Formatting Viewer Access ---${NC}"
    viewer_response=$(curl -s -b "$COOKIE_JAR" \
        -w "\n---HTTP_CODE---%{http_code}" \
        "$BASE_URL/books/book/$BOOK_ID/formatting-viewer")

    viewer_code=$(echo "$viewer_response" | grep "---HTTP_CODE---" | sed 's/---HTTP_CODE---//')
    viewer_body=$(echo "$viewer_response" | sed '/---HTTP_CODE---/d')

    if [ "$viewer_code" -eq 200 ]; then
        echo -e "${GREEN}✓ Formatting viewer accessible${NC}"
        
        # Step 3: Test formatting preview with drop caps ENABLED
        echo -e "\n${BLUE}--- Testing Drop Caps ENABLED ---${NC}"
        
        drop_caps_enabled=$(curl -s -b "$COOKIE_JAR" \
            -X POST \
            -H "Content-Type: application/json" \
            -H "Accept: application/json" \
            -d '{
                "use_drop_caps": true,
                "font_family": "Crimson Pro",
                "font_size_body": 12,
                "line_spacing": 1.5,
                "include_title_page": true,
                "include_copyright_page": true,
                "include_table_of_contents": true,
                "author_name": "Test Author",
                "use_professional_typography": true,
                "use_chapter_breaks": true
            }' \
            -w "\n---HTTP_CODE---%{http_code}" \
            "$BASE_URL/books/book/$BOOK_ID/formatting-preview")

        enabled_code=$(echo "$drop_caps_enabled" | grep "---HTTP_CODE---" | sed 's/---HTTP_CODE---//')
        enabled_body=$(echo "$drop_caps_enabled" | sed '/---HTTP_CODE---/d')

        echo "$enabled_body" > "$OUTPUT_DIR/drop_caps_enabled_response.json"
        
        if [ "$enabled_code" -eq 200 ]; then
            echo -e "${GREEN}✓ Drop caps enabled request successful${NC}"
        else
            echo -e "${RED}✗ Drop caps enabled request failed (HTTP $enabled_code)${NC}"
            echo "Response: $enabled_body"
        fi

        # Step 4: Test formatting preview with drop caps DISABLED
        echo -e "\n${BLUE}--- Testing Drop Caps DISABLED ---${NC}"
        
        drop_caps_disabled=$(curl -s -b "$COOKIE_JAR" \
            -X POST \
            -H "Content-Type: application/json" \
            -H "Accept: application/json" \
            -d '{
                "use_drop_caps": false,
                "font_family": "Crimson Pro",
                "font_size_body": 12,
                "line_spacing": 1.5,
                "include_title_page": true,
                "include_copyright_page": true,
                "include_table_of_contents": true,
                "author_name": "Test Author",
                "use_professional_typography": true,
                "use_chapter_breaks": true
            }' \
            -w "\n---HTTP_CODE---%{http_code}" \
            "$BASE_URL/books/book/$BOOK_ID/formatting-preview")

        disabled_code=$(echo "$drop_caps_disabled" | grep "---HTTP_CODE---" | sed 's/---HTTP_CODE---//')
        disabled_body=$(echo "$drop_caps_disabled" | sed '/---HTTP_CODE---/d')

        echo "$disabled_body" > "$OUTPUT_DIR/drop_caps_disabled_response.json"
        
        if [ "$disabled_code" -eq 200 ]; then
            echo -e "${GREEN}✓ Drop caps disabled request successful${NC}"
        else
            echo -e "${RED}✗ Drop caps disabled request failed (HTTP $disabled_code)${NC}"
            echo "Response: $disabled_body"
        fi

        # Step 5: Compare responses if both succeeded
        if [ "$enabled_code" -eq 200 ] && [ "$disabled_code" -eq 200 ]; then
            echo -e "\n${BLUE}--- Analyzing Drop Caps Implementation ---${NC}"
            
            # Extract HTML content from JSON responses
            python3 -c "
import json
import sys

def extract_and_analyze(filename, label):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        if 'preview_html' in data:
            html = data['preview_html']
            
            # Count drop caps patterns
            drop_cap_letter = html.count('drop-cap-letter')
            data_drop_cap = html.count('data-drop-cap')
            data_drop_cap_char = html.count('data-drop-cap-char')
            
            print(f'{label}:')
            print(f'  - HTML length: {len(html)} characters')
            print(f'  - drop-cap-letter class: {drop_cap_letter} occurrences')
            print(f'  - data-drop-cap attribute: {data_drop_cap} occurrences') 
            print(f'  - data-drop-cap-char attribute: {data_drop_cap_char} occurrences')
            
            # Show sample if found
            if drop_cap_letter > 0:
                import re
                samples = re.findall(r'<span class=\"drop-cap-letter\"[^>]*>[^<]*</span>', html)
                if samples:
                    print(f'  - Sample drop cap HTML: {samples[0]}')
            
            return {
                'html_length': len(html),
                'drop_cap_letter': drop_cap_letter,
                'data_drop_cap': data_drop_cap,
                'data_drop_cap_char': data_drop_cap_char
            }
        else:
            print(f'{label}: No preview_html found')
            print(f'  Available keys: {list(data.keys())}')
            return None
            
    except Exception as e:
        print(f'{label}: Error - {e}')
        return None

enabled_stats = extract_and_analyze('$OUTPUT_DIR/drop_caps_enabled_response.json', 'DROP CAPS ENABLED')
print()
disabled_stats = extract_and_analyze('$OUTPUT_DIR/drop_caps_disabled_response.json', 'DROP CAPS DISABLED')

if enabled_stats and disabled_stats:
    print(f'\\nCOMPARISON:')
    print(f'  HTML size difference: {enabled_stats[\"html_length\"] - disabled_stats[\"html_length\"]} chars')
    
    if enabled_stats['drop_cap_letter'] > 0 or enabled_stats['data_drop_cap'] > 0:
        print(f'  ✓ Drop caps features found in ENABLED response')
    else:
        print(f'  ✗ No drop caps features in ENABLED response')
        
    if disabled_stats['drop_cap_letter'] == 0 and disabled_stats['data_drop_cap'] == 0:
        print(f'  ✓ No drop caps features in DISABLED response (correct)')
    else:
        print(f'  ⚠ Unexpected drop caps in DISABLED response')
        
    # Final result
    if (enabled_stats['drop_cap_letter'] > 0 or enabled_stats['data_drop_cap'] > 0) and disabled_stats['drop_cap_letter'] == 0 and disabled_stats['data_drop_cap'] == 0:
        print(f'\\n🎉 SUCCESS: Drop caps functionality is working correctly!')
        sys.exit(0)
    else:
        print(f'\\n❌ FAILURE: Drop caps functionality is not working as expected')
        sys.exit(1)
"
        else
            echo -e "${RED}✗ Cannot analyze - one or both requests failed${NC}"
        fi

    else
        echo -e "${RED}✗ Cannot access formatting viewer (HTTP $viewer_code)${NC}"
        if [ ${#viewer_body} -lt 500 ]; then
            echo "Response: $viewer_body"
        fi
    fi
else
    echo -e "${RED}✗ Login failed (HTTP $login_code)${NC}"
    if [ ${#login_body} -lt 500 ]; then
        echo "Response: $login_body"
    fi
fi

echo -e "\n${BLUE}=== Files saved to: $OUTPUT_DIR ===${NC}"

# Cleanup
rm -f "$COOKIE_JAR"