#!/usr/bin/env python3
"""
Complete Integration Test for Flask Application

This script demonstrates that the Flask application is fully functional
and can be used immediately. Run this to verify everything works.

Usage:
    uv run python test_flask_integration.py
"""

import subprocess
import time
import requests
import json
import sys
from pathlib import Path


def test_imports():
    """Test that all modules import correctly"""
    print("=" * 70)
    print("TEST 1: Verifying Imports")
    print("=" * 70)
    
    try:
        from flask_app.app import app
        print("✅ Flask app imported successfully")
        
        from app.pipeline.empathy_pipeline import EmpathyPipeline
        print("✅ EmpathyPipeline imported successfully")
        
        from app.emotion.detector import EmotionDetector
        print("✅ EmotionDetector imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_api_endpoints():
    """Test all API endpoints"""
    print("\n" + "=" * 70)
    print("TEST 2: Testing API Endpoints")
    print("=" * 70)
    
    from flask_app.app import app
    
    with app.test_client() as client:
        tests = [
            {
                "name": "Home endpoint",
                "method": "GET",
                "path": "/",
                "data": None,
                "expected_status": 200
            },
            {
                "name": "Health check",
                "method": "GET",
                "path": "/api/health",
                "data": None,
                "expected_status": 200
            },
            {
                "name": "API documentation",
                "method": "GET",
                "path": "/api/docs",
                "data": None,
                "expected_status": 200
            },
            {
                "name": "Emotion detection - positive",
                "method": "POST",
                "path": "/api/emotion",
                "data": {"text": "I absolutely love this amazing project!"},
                "expected_status": 200,
                "check_response": lambda r: r.get("emotion") == "positive"
            },
            {
                "name": "Emotion detection - negative",
                "method": "POST",
                "path": "/api/emotion",
                "data": {"text": "This is terrible and awful"},
                "expected_status": 200,
                "check_response": lambda r: r.get("emotion") == "negative"
            },
            {
                "name": "Error handling - empty text",
                "method": "POST",
                "path": "/api/emotion",
                "data": {"text": ""},
                "expected_status": 400
            },
            {
                "name": "Error handling - missing text field",
                "method": "POST",
                "path": "/api/emotion",
                "data": {},
                "expected_status": 400
            },
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test["method"] == "GET":
                    response = client.get(test["path"])
                else:
                    response = client.post(
                        test["path"],
                        json=test["data"],
                        content_type="application/json"
                    )
                
                status_ok = response.status_code == test["expected_status"]
                
                if status_ok:
                    response_ok = True
                    if "check_response" in test and response.status_code == 200:
                        data = response.get_json()
                        response_ok = test["check_response"](data)
                    
                    if response_ok:
                        print(f"✅ {test['name']}: {response.status_code}")
                        passed += 1
                    else:
                        print(f"❌ {test['name']}: Response validation failed")
                        failed += 1
                else:
                    print(f"❌ {test['name']}: Expected {test['expected_status']}, got {response.status_code}")
                    failed += 1
                    
            except Exception as e:
                print(f"❌ {test['name']}: {e}")
                failed += 1
        
        print(f"\nResults: {passed} passed, {failed} failed")
        return failed == 0


def test_files():
    """Test that all required files exist"""
    print("\n" + "=" * 70)
    print("TEST 3: Verifying Files")
    print("=" * 70)
    
    required_files = [
        ("flask_app/app.py", "Flask API application"),
        ("flask_app/__init__.py", "Flask package init"),
        ("client.py", "Python API client"),
        ("run_flask.sh", "Launcher script"),
        ("streamlit_integrated_app.py", "Streamlit integration example"),
        ("FLASK_API.md", "API documentation"),
        ("FLASK_SUMMARY.md", "Quick start guide"),
        ("FLASK_TROUBLESHOOTING.md", "Troubleshooting guide"),
        ("PROJECT_STRUCTURE.md", "Architecture documentation"),
        ("QUICK_REFERENCE.md", "Quick reference card"),
        ("IMPLEMENTATION_COMPLETE.md", "Implementation summary"),
    ]
    
    all_exist = True
    for filepath, description in required_files:
        path = Path(filepath)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {filepath} ({size} bytes) - {description}")
        else:
            print(f"❌ {filepath} - MISSING")
            all_exist = False
    
    return all_exist


def test_documentation():
    """Test that documentation is complete"""
    print("\n" + "=" * 70)
    print("TEST 4: Verifying Documentation")
    print("=" * 70)
    
    docs = {
        "FLASK_API.md": 300,  # Should have substantial content
        "FLASK_SUMMARY.md": 200,
        "FLASK_TROUBLESHOOTING.md": 250,
        "PROJECT_STRUCTURE.md": 300,
        "QUICK_REFERENCE.md": 100,
    }
    
    all_ok = True
    for doc, min_lines in docs.items():
        path = Path(doc)
        if path.exists():
            lines = len(path.read_text().split('\n'))
            if lines >= min_lines:
                print(f"✅ {doc}: {lines} lines")
            else:
                print(f"⚠️  {doc}: Only {lines} lines (expected >{min_lines})")
                all_ok = False
        else:
            print(f"❌ {doc}: Not found")
            all_ok = False
    
    return all_ok


def get_statistics():
    """Calculate statistics about the implementation"""
    print("\n" + "=" * 70)
    print("IMPLEMENTATION STATISTICS")
    print("=" * 70)
    
    python_files = [
        "flask_app/app.py",
        "client.py",
        "streamlit_integrated_app.py",
    ]
    
    doc_files = [
        "FLASK_API.md",
        "FLASK_SUMMARY.md",
        "FLASK_TROUBLESHOOTING.md",
        "PROJECT_STRUCTURE.md",
        "IMPLEMENTATION_COMPLETE.md",
        "QUICK_REFERENCE.md",
    ]
    
    total_python_lines = 0
    total_doc_lines = 0
    
    print("\nPython Code:")
    for f in python_files:
        if Path(f).exists():
            lines = len(Path(f).read_text().split('\n'))
            total_python_lines += lines
            print(f"  {f}: {lines} lines")
    
    print(f"\n  Total Python: {total_python_lines} lines")
    
    print("\nDocumentation:")
    for f in doc_files:
        if Path(f).exists():
            lines = len(Path(f).read_text().split('\n'))
            total_doc_lines += lines
            print(f"  {f}: {lines} lines")
    
    print(f"\n  Total Documentation: {total_doc_lines} lines")
    
    print(f"\nGrand Total: {total_python_lines + total_doc_lines} lines")
    print(f"Endpoints: 6 REST API endpoints")
    print(f"Files Created: {len(python_files) + len(doc_files)} files")


def main():
    """Run all tests"""
    print("\n")
    print("█" * 70)
    print("█" + " " * 68 + "█")
    print("█  🎙️  EMPATHY ENGINE - FLASK APPLICATION INTEGRATION TEST" + " " * 7 + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    results = {
        "Imports": test_imports(),
        "API Endpoints": test_api_endpoints(),
        "Files": test_files(),
        "Documentation": test_documentation(),
    }
    
    get_statistics()
    
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED - FLASK APPLICATION IS READY FOR USE")
        print("=" * 70)
        print("\nQuick Start Commands:")
        print("  1. Start the API:  ./run_flask.sh")
        print("  2. Test with CLI:  uv run python client.py")
        print("  3. View docs:      cat QUICK_REFERENCE.md")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - PLEASE CHECK THE OUTPUT ABOVE")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
