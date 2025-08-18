#!/usr/bin/env python3
"""
Direct Drop Caps Test for Buko AI Professional Formatting Service
This script tests the drop caps functionality directly at the service level,
bypassing web authentication and form handling.
"""

import sys
import os
import json
import re
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_drop_caps_service():
    """Test drop caps functionality directly using the service layer"""
    print("🧪 Direct Drop Caps Service Test")
    print("=" * 50)
    
    try:
        # Initialize Flask app context
        from app import create_app
        from app.models.book_generation import BookGeneration
        from app.services.professional_formatting_service import (
            ProfessionalFormattingService, 
            ProfessionalFormattingOptions
        )
        
        app = create_app()
        
        with app.app_context():
            print("✅ Flask app context initialized")
            
            # Get the test book from database
            book = BookGeneration.query.filter_by(id=33).first()
            if not book:
                print("❌ Test book (ID: 33) not found in database")
                return False
                
            print(f"✅ Found test book: {book.title}")
            print(f"   - Status: {book.status}")
            print(f"   - Content length: {len(book.content) if book.content else 0:,} chars")
            
            if not book.content and not book.content_html:
                print("❌ Book has no content to format")
                return False
            
            # Initialize formatting service
            formatting_service = ProfessionalFormattingService()
            print("✅ Professional formatting service initialized")
            
            # Test 1: Formatting with DROP CAPS ENABLED
            print("\n🎨 Testing DROP CAPS ENABLED...")
            
            enabled_options = ProfessionalFormattingOptions(
                include_title_page=True,
                include_copyright_page=True,
                include_table_of_contents=True,
                include_about_author=True,
                author_name="Test Author",
                font_family="Crimson Pro",
                font_size_body=12,
                line_spacing=1.5,
                use_professional_typography=True,
                use_drop_caps=True,  # ← KEY: ENABLED
                use_chapter_breaks=True
            )
            
            try:
                enabled_result = formatting_service.format_for_commercial_distribution(book, enabled_options)
                
                if enabled_result and enabled_result.get('formatted_content'):
                    print("   ✅ Drop caps enabled formatting successful")
                    enabled_html = enabled_result['formatted_content']
                    print(f"   - Generated HTML length: {len(enabled_html):,} characters")
                else:
                    print("   ❌ Drop caps enabled formatting failed")
                    print(f"   - Result keys: {list(enabled_result.keys()) if enabled_result else 'None'}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Drop caps enabled formatting error: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            # Test 2: Formatting with DROP CAPS DISABLED
            print("\n🎨 Testing DROP CAPS DISABLED...")
            
            disabled_options = ProfessionalFormattingOptions(
                include_title_page=True,
                include_copyright_page=True,
                include_table_of_contents=True,
                include_about_author=True,
                author_name="Test Author",
                font_family="Crimson Pro",
                font_size_body=12,
                line_spacing=1.5,
                use_professional_typography=True,
                use_drop_caps=False,  # ← KEY: DISABLED
                use_chapter_breaks=True
            )
            
            try:
                disabled_result = formatting_service.format_for_commercial_distribution(book, disabled_options)
                
                if disabled_result and disabled_result.get('formatted_content'):
                    print("   ✅ Drop caps disabled formatting successful")
                    disabled_html = disabled_result['formatted_content']
                    print(f"   - Generated HTML length: {len(disabled_html):,} characters")
                else:
                    print("   ❌ Drop caps disabled formatting failed")
                    print(f"   - Result keys: {list(disabled_result.keys()) if disabled_result else 'None'}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Drop caps disabled formatting error: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            # Test 3: Analyze the differences
            print("\n🔍 Analyzing drop caps implementation...")
            
            def analyze_html(html, label):
                """Analyze HTML for drop caps patterns"""
                # Count different drop caps patterns
                drop_cap_letter_count = html.count('drop-cap-letter')
                data_drop_cap_count = html.count('data-drop-cap')
                data_drop_cap_char_count = html.count('data-drop-cap-char')
                
                # Look for specific drop caps CSS classes or attributes
                drop_cap_spans = re.findall(r'<span class="drop-cap-letter"[^>]*>[^<]*</span>', html)
                data_drop_cap_attrs = re.findall(r'data-drop-cap="[^"]*"', html)
                data_drop_cap_char_attrs = re.findall(r'data-drop-cap-char="[^"]*"', html)
                
                print(f"   {label}:")
                print(f"     - HTML length: {len(html):,} characters")
                print(f"     - 'drop-cap-letter' class occurrences: {drop_cap_letter_count}")
                print(f"     - 'data-drop-cap' attribute occurrences: {data_drop_cap_count}")
                print(f"     - 'data-drop-cap-char' attribute occurrences: {data_drop_cap_char_count}")
                
                if drop_cap_spans:
                    print(f"     - Sample drop cap spans: {drop_cap_spans[:3]}")  # Show first 3
                    
                if data_drop_cap_attrs:
                    print(f"     - Sample data-drop-cap attributes: {data_drop_cap_attrs[:3]}")
                
                return {
                    'html_length': len(html),
                    'drop_cap_letter_count': drop_cap_letter_count,
                    'data_drop_cap_count': data_drop_cap_count,
                    'data_drop_cap_char_count': data_drop_cap_char_count,
                    'drop_cap_spans': drop_cap_spans,
                    'data_drop_cap_attrs': data_drop_cap_attrs,
                    'html': html
                }
            
            enabled_stats = analyze_html(enabled_html, "DROP CAPS ENABLED")
            disabled_stats = analyze_html(disabled_html, "DROP CAPS DISABLED")
            
            # Test 4: Compare results and conclusion
            print(f"\n📊 COMPARISON RESULTS:")
            html_size_diff = enabled_stats['html_length'] - disabled_stats['html_length']
            print(f"   - HTML size difference: {html_size_diff:,} characters")
            
            # Check if drop caps are properly implemented
            enabled_has_drop_caps = (
                enabled_stats['drop_cap_letter_count'] > 0 or 
                enabled_stats['data_drop_cap_count'] > 0 or
                len(enabled_stats['drop_cap_spans']) > 0
            )
            
            disabled_has_drop_caps = (
                disabled_stats['drop_cap_letter_count'] > 0 or 
                disabled_stats['data_drop_cap_count'] > 0 or
                len(disabled_stats['drop_cap_spans']) > 0
            )
            
            print(f"   - Drop caps in ENABLED response: {'✅ Found' if enabled_has_drop_caps else '❌ Not found'}")
            print(f"   - Drop caps in DISABLED response: {'❌ Found (unexpected)' if disabled_has_drop_caps else '✅ Not found (correct)'}")
            
            # Save results for inspection
            output_dir = "/tmp/drop_caps_test"
            os.makedirs(output_dir, exist_ok=True)
            
            with open(f"{output_dir}/drop_caps_enabled_direct.html", 'w', encoding='utf-8') as f:
                f.write(enabled_html)
            with open(f"{output_dir}/drop_caps_disabled_direct.html", 'w', encoding='utf-8') as f:
                f.write(disabled_html)
            
            # Create detailed analysis report
            analysis = {
                'test_type': 'direct_service_test',
                'book_id': book.id,
                'book_title': book.title,
                'enabled_stats': {k: v for k, v in enabled_stats.items() if k != 'html'},
                'disabled_stats': {k: v for k, v in disabled_stats.items() if k != 'html'},
                'comparison': {
                    'html_size_difference': html_size_diff,
                    'enabled_has_drop_caps': enabled_has_drop_caps,
                    'disabled_has_drop_caps': disabled_has_drop_caps,
                    'test_passed': enabled_has_drop_caps and not disabled_has_drop_caps
                }
            }
            
            with open(f"{output_dir}/drop_caps_analysis.json", 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            print(f"\n📁 Files saved to: {output_dir}")
            
            # Final verdict
            if enabled_has_drop_caps and not disabled_has_drop_caps:
                print(f"\n🎉 SUCCESS: Drop caps functionality is working correctly!")
                print(f"   ✅ Drop caps appear when use_drop_caps=True")
                print(f"   ✅ Drop caps are absent when use_drop_caps=False")
                
                # Show some specific evidence
                if enabled_stats['drop_cap_spans']:
                    print(f"   📝 Example drop cap HTML: {enabled_stats['drop_cap_spans'][0]}")
                    
                return True
            else:
                print(f"\n❌ FAILURE: Drop caps functionality is not working as expected")
                if not enabled_has_drop_caps:
                    print(f"   ❌ No drop caps found when use_drop_caps=True")
                if disabled_has_drop_caps:
                    print(f"   ❌ Drop caps found when use_drop_caps=False (should be absent)")
                    
                return False
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running this from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_drop_caps_service()
    sys.exit(0 if success else 1)