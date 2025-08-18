#!/bin/bash

# Drop Caps Testing Script for Buko AI Professional Formatting
# This script tests if drop caps modifications are working correctly

set -e  # Exit on any error

# Configuration
BASE_URL="http://localhost:5001"
USER_EMAIL="admin@buko-ai.com"
USER_PASSWORD="admin123"  # Test password
BOOK_ID="33"
COOKIE_JAR="/tmp/buko_cookies.txt"
OUTPUT_DIR="/tmp/drop_caps_test"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}  Drop Caps Functionality Test for Buko AI${NC}"
echo -e "${BLUE}===================================================${NC}"
echo -e "${YELLOW}Base URL: $BASE_URL${NC}"
echo -e "${YELLOW}User: $USER_EMAIL${NC}"
echo -e "${YELLOW}Book ID: $BOOK_ID${NC}"
echo -e "${YELLOW}Output Directory: $OUTPUT_DIR${NC}"
echo ""

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}--- $1 ---${NC}"
}

# Function to check HTTP status
check_status() {
    local response_code=$1
    local expected=$2
    local description=$3
    
    if [ "$response_code" -eq "$expected" ]; then
        echo -e "${GREEN}✓ $description: HTTP $response_code (Success)${NC}"
        return 0
    else
        echo -e "${RED}✗ $description: HTTP $response_code (Expected: $expected)${NC}"
        return 1
    fi
}

# Function to check if content contains pattern
check_pattern() {
    local content=$1
    local pattern=$2
    local description=$3
    
    if echo "$content" | grep -q "$pattern"; then
        echo -e "${GREEN}✓ $description: Pattern found${NC}"
        return 0
    else
        echo -e "${RED}✗ $description: Pattern NOT found${NC}"
        return 1
    fi
}

# Step 1: Check if application is running
print_section "Checking Application Status"
if curl -s --connect-timeout 5 "$BASE_URL" > /dev/null; then
    echo -e "${GREEN}✓ Application is running${NC}"
else
    echo -e "${RED}✗ Application is not accessible at $BASE_URL${NC}"
    exit 1
fi

# Step 2: Get CSRF token from login page
print_section "Getting CSRF Token"
login_page=$(curl -s -c "$COOKIE_JAR" "$BASE_URL/auth/login")
csrf_token=$(echo "$login_page" | grep -o 'name="csrf_token"[^>]*value="[^"]*"' | sed 's/.*value="\([^"]*\)".*/\1/' | head -1)

if [ -z "$csrf_token" ]; then
    echo -e "${RED}✗ Could not extract CSRF token${NC}"
    exit 1
else
    echo -e "${GREEN}✓ CSRF Token extracted: ${csrf_token:0:20}...${NC}"
fi

# Step 3: Login
print_section "Logging In"
login_response=$(curl -s -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
    -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "csrf_token=$csrf_token&email=$USER_EMAIL&password=$USER_PASSWORD&remember_me=false" \
    -w "%{http_code}" \
    "$BASE_URL/auth/login")

login_code=$(echo "$login_response" | tail -n1)
login_body=$(echo "$login_response" | head -n -1)

if [ "$login_code" -eq 302 ] || [ "$login_code" -eq 200 ]; then
    echo -e "${GREEN}✓ Login successful (HTTP $login_code)${NC}"
else
    echo -e "${RED}✗ Login failed (HTTP $login_code)${NC}"
    echo -e "${RED}Response: $login_body${NC}"
    exit 1
fi

# Step 4: Verify access to formatting viewer
print_section "Accessing Formatting Viewer"
viewer_response=$(curl -s -b "$COOKIE_JAR" \
    -w "%{http_code}" \
    "$BASE_URL/books/book/$BOOK_ID/formatting-viewer")

viewer_code=$(echo "$viewer_response" | tail -n1)
viewer_body=$(echo "$viewer_response" | head -n -1)

check_status "$viewer_code" 200 "Formatting viewer access"

# Step 5: Extract new CSRF token from formatting viewer
csrf_token_viewer=$(echo "$viewer_body" | grep -o 'name="csrf_token"[^>]*value="[^"]*"' | sed 's/.*value="\([^"]*\)".*/\1/' | head -1)
if [ -z "$csrf_token_viewer" ]; then
    # Try alternative CSRF extraction methods
    csrf_token_viewer=$(echo "$viewer_body" | grep -o '"csrf_token"[^}]*"[^"]*"' | sed 's/.*"\([^"]*\)".*/\1/' | tail -1)
fi

if [ -n "$csrf_token_viewer" ]; then
    echo -e "${GREEN}✓ Viewer CSRF Token extracted: ${csrf_token_viewer:0:20}...${NC}"
    csrf_token="$csrf_token_viewer"
else
    echo -e "${YELLOW}⚠ Using original CSRF token${NC}"
fi

# Step 6: Test formatting preview with DROP CAPS ENABLED
print_section "Testing Drop Caps ENABLED (use_drop_caps=true)"

drop_caps_enabled_response=$(curl -s -b "$COOKIE_JAR" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-CSRFToken: $csrf_token" \
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

enabled_code=$(echo "$drop_caps_enabled_response" | grep "---HTTP_CODE---" | sed 's/---HTTP_CODE---//')
enabled_body=$(echo "$drop_caps_enabled_response" | sed '/---HTTP_CODE---/d')

echo "$enabled_body" > "$OUTPUT_DIR/drop_caps_enabled_response.json"
check_status "$enabled_code" 200 "Drop caps enabled request"

# Step 7: Test formatting preview with DROP CAPS DISABLED
print_section "Testing Drop Caps DISABLED (use_drop_caps=false)"

drop_caps_disabled_response=$(curl -s -b "$COOKIE_JAR" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-CSRFToken: $csrf_token" \
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

disabled_code=$(echo "$drop_caps_disabled_response" | grep "---HTTP_CODE---" | sed 's/---HTTP_CODE---//')
disabled_body=$(echo "$drop_caps_disabled_response" | sed '/---HTTP_CODE---/d')

echo "$disabled_body" > "$OUTPUT_DIR/drop_caps_disabled_response.json"
check_status "$disabled_code" 200 "Drop caps disabled request"

# Step 8: Extract and save HTML content from both responses
print_section "Extracting HTML Content"

# Extract preview_html from JSON responses using python
python3 -c "
import json
import sys

def extract_html(filename, output_filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'preview_html' in data:
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(data['preview_html'])
            print(f'✓ HTML extracted to {output_filename}')
            return True
        else:
            print(f'✗ No preview_html found in {filename}')
            print(f'Available keys: {list(data.keys())}')
            return False
    except Exception as e:
        print(f'✗ Error processing {filename}: {e}')
        return False

# Extract HTML from both responses
success1 = extract_html('$OUTPUT_DIR/drop_caps_enabled_response.json', '$OUTPUT_DIR/drop_caps_enabled.html')
success2 = extract_html('$OUTPUT_DIR/drop_caps_disabled_response.json', '$OUTPUT_DIR/drop_caps_disabled.html')

sys.exit(0 if success1 and success2 else 1)
"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to extract HTML content${NC}"
    exit 1
fi

# Step 9: Search for drop caps patterns
print_section "Searching for Drop Caps Patterns"

echo -e "\n${YELLOW}Drop Caps ENABLED Response:${NC}"
enabled_html=$(cat "$OUTPUT_DIR/drop_caps_enabled.html" 2>/dev/null || echo "")

if [ -n "$enabled_html" ]; then
    echo -e "  ${BLUE}File size: $(wc -c < "$OUTPUT_DIR/drop_caps_enabled.html") bytes${NC}"
    
    # Search for drop-cap-letter class
    drop_cap_letter_count=$(echo "$enabled_html" | grep -o 'drop-cap-letter' | wc -l)
    echo -e "  ${BLUE}drop-cap-letter class occurrences: $drop_cap_letter_count${NC}"
    
    # Search for data-drop-cap attribute
    data_drop_cap_count=$(echo "$enabled_html" | grep -o 'data-drop-cap' | wc -l)
    echo -e "  ${BLUE}data-drop-cap attribute occurrences: $data_drop_cap_count${NC}"
    
    # Search for data-drop-cap-char attribute
    data_drop_cap_char_count=$(echo "$enabled_html" | grep -o 'data-drop-cap-char' | wc -l)
    echo -e "  ${BLUE}data-drop-cap-char attribute occurrences: $data_drop_cap_char_count${NC}"
    
    # Show sample drop cap HTML if found
    if [ $drop_cap_letter_count -gt 0 ]; then
        echo -e "\n  ${GREEN}Sample drop cap HTML:${NC}"
        echo "$enabled_html" | grep -o '<span class="drop-cap-letter"[^>]*>[^<]*</span>' | head -3 | sed 's/^/    /'
    fi
    
    if [ $data_drop_cap_count -gt 0 ]; then
        echo -e "\n  ${GREEN}Sample data-drop-cap attributes:${NC}"
        echo "$enabled_html" | grep -o 'data-drop-cap="[^"]*"' | head -3 | sed 's/^/    /'
    fi
else
    echo -e "  ${RED}✗ No HTML content found in enabled response${NC}"
fi

echo -e "\n${YELLOW}Drop Caps DISABLED Response:${NC}"
disabled_html=$(cat "$OUTPUT_DIR/drop_caps_disabled.html" 2>/dev/null || echo "")

if [ -n "$disabled_html" ]; then
    echo -e "  ${BLUE}File size: $(wc -c < "$OUTPUT_DIR/drop_caps_disabled.html") bytes${NC}"
    
    # Search for drop-cap-letter class
    drop_cap_letter_count_disabled=$(echo "$disabled_html" | grep -o 'drop-cap-letter' | wc -l)
    echo -e "  ${BLUE}drop-cap-letter class occurrences: $drop_cap_letter_count_disabled${NC}"
    
    # Search for data-drop-cap attribute
    data_drop_cap_count_disabled=$(echo "$disabled_html" | grep -o 'data-drop-cap' | wc -l)
    echo -e "  ${BLUE}data-drop-cap attribute occurrences: $data_drop_cap_count_disabled${NC}"
    
    # Search for data-drop-cap-char attribute
    data_drop_cap_char_count_disabled=$(echo "$disabled_html" | grep -o 'data-drop-cap-char' | wc -l)
    echo -e "  ${BLUE}data-drop-cap-char attribute occurrences: $data_drop_cap_char_count_disabled${NC}"
else
    echo -e "  ${RED}✗ No HTML content found in disabled response${NC}"
fi

# Step 10: Compare responses and show differences
print_section "Comparing Responses"

if [ -n "$enabled_html" ] && [ -n "$disabled_html" ]; then
    # Calculate differences
    enabled_size=$(echo "$enabled_html" | wc -c)
    disabled_size=$(echo "$disabled_html" | wc -c)
    size_diff=$((enabled_size - disabled_size))
    
    echo -e "  ${BLUE}Size comparison:${NC}"
    echo -e "    Enabled:  $enabled_size bytes"
    echo -e "    Disabled: $disabled_size bytes"
    echo -e "    Difference: $size_diff bytes"
    
    # Create diff file
    diff -u "$OUTPUT_DIR/drop_caps_disabled.html" "$OUTPUT_DIR/drop_caps_enabled.html" > "$OUTPUT_DIR/html_diff.txt" 2>/dev/null || true
    diff_lines=$(wc -l < "$OUTPUT_DIR/html_diff.txt")
    
    if [ $diff_lines -gt 0 ]; then
        echo -e "\n  ${GREEN}✓ Differences found ($diff_lines lines in diff)${NC}"
        echo -e "  ${BLUE}Diff saved to: $OUTPUT_DIR/html_diff.txt${NC}"
        
        # Show first few differences
        echo -e "\n  ${YELLOW}First few differences:${NC}"
        head -20 "$OUTPUT_DIR/html_diff.txt" | sed 's/^/    /'
        
        if [ $diff_lines -gt 20 ]; then
            echo -e "    ${BLUE}... ($(($diff_lines - 20)) more lines)${NC}"
        fi
    else
        echo -e "\n  ${RED}✗ No differences found between enabled and disabled responses${NC}"
    fi
    
    # Specific drop caps analysis
    echo -e "\n  ${YELLOW}Drop Caps Specific Analysis:${NC}"
    
    if [ "$drop_cap_letter_count" -gt 0 ] || [ "$data_drop_cap_count" -gt 0 ]; then
        echo -e "    ${GREEN}✓ Drop caps features found in ENABLED response${NC}"
    else
        echo -e "    ${RED}✗ No drop caps features found in ENABLED response${NC}"
    fi
    
    if [ "$drop_cap_letter_count_disabled" -eq 0 ] && [ "$data_drop_cap_count_disabled" -eq 0 ]; then
        echo -e "    ${GREEN}✓ No drop caps features in DISABLED response (as expected)${NC}"
    else
        echo -e "    ${YELLOW}⚠ Unexpected drop caps features found in DISABLED response${NC}"
    fi
    
else
    echo -e "  ${RED}✗ Cannot compare - missing HTML content${NC}"
fi

# Step 11: Generate summary report
print_section "Test Summary Report"

echo -e "\n${BLUE}Test Results Summary:${NC}"
echo -e "===================="

# Count successes and failures
total_tests=7
passed_tests=0

# Test results
test_results=(
    "Application Access:OK"
    "Login:OK"
    "Formatting Viewer Access:$([[ $viewer_code -eq 200 ]] && echo "OK" || echo "FAIL")"
    "Drop Caps Enabled Request:$([[ $enabled_code -eq 200 ]] && echo "OK" || echo "FAIL")"
    "Drop Caps Disabled Request:$([[ $disabled_code -eq 200 ]] && echo "OK" || echo "FAIL")"
    "HTML Content Extraction:$([[ -n "$enabled_html" && -n "$disabled_html" ]] && echo "OK" || echo "FAIL")"
    "Drop Caps Functionality:$([[ $drop_cap_letter_count -gt 0 || $data_drop_cap_count -gt 0 ]] && echo "OK" || echo "FAIL")"
)

for result in "${test_results[@]}"; do
    test_name=$(echo "$result" | cut -d: -f1)
    test_status=$(echo "$result" | cut -d: -f2)
    
    if [ "$test_status" = "OK" ]; then
        echo -e "  ${GREEN}✓ $test_name${NC}"
        ((passed_tests++))
    else
        echo -e "  ${RED}✗ $test_name${NC}"
    fi
done

echo -e "\n${BLUE}Overall Result: $passed_tests/$total_tests tests passed${NC}"

if [ $passed_tests -eq $total_tests ]; then
    echo -e "${GREEN}🎉 All tests passed! Drop caps functionality is working correctly.${NC}"
    exit_code=0
else
    echo -e "${RED}❌ Some tests failed. Check the output above for details.${NC}"
    exit_code=1
fi

# Step 12: Show file locations
print_section "Generated Files"
echo -e "All test files saved to: ${BLUE}$OUTPUT_DIR${NC}"
echo -e "  - drop_caps_enabled_response.json"
echo -e "  - drop_caps_disabled_response.json" 
echo -e "  - drop_caps_enabled.html"
echo -e "  - drop_caps_disabled.html"
echo -e "  - html_diff.txt"

# Cleanup
rm -f "$COOKIE_JAR"

echo -e "\n${BLUE}===================================================${NC}"
echo -e "${BLUE}  Test completed${NC}"
echo -e "${BLUE}===================================================${NC}"

exit $exit_code