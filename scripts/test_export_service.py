#!/usr/bin/env python3
"""
Test script for the Book Export Service.
Tests all export formats and platforms.
"""

import os
import sys
import tempfile
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MockBook:
    """Mock book object for testing."""
    id: int = 1
    uuid: str = "test-uuid-123"
    title: str = "Test Book Title"
    genre: str = "fiction"
    language: str = "es"
    target_audience: str = "adult"
    format_size: str = "letter"
    line_spacing: str = "medium"
    content: str = """# Test Book Title

## Capítulo 1: Introducción

Este es el primer capítulo del libro de prueba. Contiene múltiples párrafos para probar el formateo.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

### Sección 1.1: Subsección

Esta es una subsección dentro del capítulo. Aquí podemos probar el formateo de subtítulos.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

## Capítulo 2: Desarrollo

Este es el segundo capítulo, que continúa la historia o el contenido del libro.

Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

### Sección 2.1: Más contenido

Aquí hay más contenido para probar la estructura jerárquica del documento.

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium.

## Capítulo 3: Conclusión

El capítulo final del libro, que proporciona un cierre al contenido.

Totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt.
"""


def test_export_service():
    """Test the export service with all formats and platforms."""
    try:
        # Import after adding to path
        from app.services.export_service import BookExportService, ExportFormat, ExportPlatform
        
        # Create mock Flask app context
        from flask import Flask
        app = Flask(__name__)
        app.config['STORAGE_PATH'] = tempfile.mkdtemp()
        
        with app.app_context():
            # Create export service
            export_service = BookExportService()
            
            # Create mock book
            book = MockBook()
            
            print(f"🧪 Testing Book Export Service")
            print(f"📁 Storage directory: {app.config['STORAGE_PATH']}")
            print(f"📖 Test book: {book.title}")
            print("-" * 60)
            
            # Test each format with standard platform
            formats_to_test = [
                (ExportFormat.PDF, "PDF"),
                (ExportFormat.EPUB, "EPUB"),
                (ExportFormat.DOCX, "DOCX"),
                (ExportFormat.TXT, "TXT")
            ]
            
            platforms_to_test = [
                (ExportPlatform.STANDARD, "Standard"),
                (ExportPlatform.AMAZON_KDP, "Amazon KDP"),
                (ExportPlatform.GOOGLE_PLAY, "Google Play"),
                (ExportPlatform.APPLE_BOOKS, "Apple Books"),
                (ExportPlatform.KOBO, "Kobo"),
                (ExportPlatform.SMASHWORDS, "Smashwords"),
                (ExportPlatform.GUMROAD, "Gumroad"),
                (ExportPlatform.PAYHIP, "Payhip")
            ]
            
            results = {
                'successful': [],
                'failed': [],
                'skipped': []
            }
            
            # Test standard format for each format type
            print("🔄 Testing Standard Formats...")
            for export_format, format_name in formats_to_test:
                try:
                    print(f"  📄 Testing {format_name}...", end=" ")
                    file_path = export_service.export_book(book, export_format, ExportPlatform.STANDARD)
                    
                    if file_path and os.path.exists(file_path):
                        size = os.path.getsize(file_path)
                        print(f"✅ SUCCESS ({size:,} bytes)")
                        results['successful'].append(f"{format_name} (Standard)")
                    else:
                        print(f"❌ FAILED (No file generated)")
                        results['failed'].append(f"{format_name} (Standard)")
                        
                except Exception as e:
                    print(f"❌ ERROR: {str(e)}")
                    results['failed'].append(f"{format_name} (Standard) - {str(e)}")
            
            print()
            
            # Test platform-specific formats (only PDF, EPUB, DOCX)
            print("🔄 Testing Platform-Specific Formats...")
            platform_formats = [(ExportFormat.PDF, "PDF"), (ExportFormat.EPUB, "EPUB"), (ExportFormat.DOCX, "DOCX")]
            
            for platform, platform_name in platforms_to_test[1:]:  # Skip standard as already tested
                print(f"  🏪 Platform: {platform_name}")
                
                for export_format, format_name in platform_formats:
                    try:
                        print(f"    📄 {format_name}...", end=" ")
                        file_path = export_service.export_book(book, export_format, platform)
                        
                        if file_path and os.path.exists(file_path):
                            size = os.path.getsize(file_path)
                            print(f"✅ SUCCESS ({size:,} bytes)")
                            results['successful'].append(f"{platform_name} - {format_name}")
                        else:
                            print(f"❌ FAILED")
                            results['failed'].append(f"{platform_name} - {format_name}")
                            
                    except Exception as e:
                        print(f"❌ ERROR: {str(e)[:50]}...")
                        results['failed'].append(f"{platform_name} - {format_name}")
            
            print()
            print("-" * 60)
            print("📊 RESULTS SUMMARY:")
            print(f"✅ Successful: {len(results['successful'])}")
            print(f"❌ Failed: {len(results['failed'])}")
            print(f"⏭️  Skipped: {len(results['skipped'])}")
            
            if results['successful']:
                print("\n✅ SUCCESSFUL EXPORTS:")
                for success in results['successful']:
                    print(f"  • {success}")
            
            if results['failed']:
                print("\n❌ FAILED EXPORTS:")
                for failure in results['failed']:
                    print(f"  • {failure}")
            
            # Test cover generation
            print("\n🎨 Testing Cover Generation...")
            try:
                from app.services.export_service import PlatformConfig
                config = PlatformConfig.CONFIGS[ExportPlatform.STANDARD]
                cover_path = export_service._generate_cover(book, config)
                
                if cover_path and os.path.exists(cover_path):
                    size = os.path.getsize(cover_path)
                    print(f"✅ Cover generated successfully ({size:,} bytes)")
                else:
                    print("❌ Cover generation failed")
                    
            except Exception as e:
                print(f"❌ Cover generation error: {str(e)}")
            
            print(f"\n🎉 Testing completed!")
            print(f"📁 Generated files are in: {app.config['STORAGE_PATH']}")
            
            return len(results['failed']) == 0
            
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure you're running this from the project root and all dependencies are installed.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def test_dependencies():
    """Test if all required dependencies are available."""
    print("🔍 Checking Dependencies...")
    
    dependencies = [
        ('reportlab', 'ReportLab for PDF generation'),
        ('ebooklib', 'EbookLib for EPUB generation'),
        ('docx', 'python-docx for DOCX generation'),
        ('PIL', 'Pillow for image processing'),
    ]
    
    missing = []
    
    for dep, description in dependencies:
        try:
            __import__(dep)
            print(f"  ✅ {dep} - {description}")
        except ImportError:
            print(f"  ❌ {dep} - {description} (MISSING)")
            missing.append(dep)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Install them with: pip install reportlab ebooklib python-docx Pillow")
        return False
    else:
        print("\n✅ All dependencies are available!")
        return True


if __name__ == "__main__":
    print("📚 Book Export Service Test Suite")
    print("=" * 60)
    
    # Check dependencies first
    if not test_dependencies():
        sys.exit(1)
    
    print()
    
    # Run export tests
    if test_export_service():
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)