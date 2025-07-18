#!/usr/bin/env python3
"""
Test script to verify deployment readiness
"""
import os
import json

def test_app_import():
    """Test that the Flask app can be imported"""
    try:
        import app
        print("✓ App imports successfully")
        return True
    except Exception as e:
        print(f"✗ App import failed: {e}")
        return False

def test_vercel_config():
    """Test that vercel.json exists and is valid"""
    try:
        if not os.path.exists('vercel.json'):
            print("✗ vercel.json not found")
            return False
        
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        # Check required fields
        if 'version' not in config:
            print("✗ vercel.json missing version field")
            return False
            
        if 'builds' not in config:
            print("✗ vercel.json missing builds field")
            return False
            
        print("✓ vercel.json is valid")
        return True
    except Exception as e:
        print(f"✗ vercel.json validation failed: {e}")
        return False

def test_requirements():
    """Test that requirements.txt exists"""
    if not os.path.exists('requirements.txt'):
        print("✗ requirements.txt not found")
        return False
    
    print("✓ requirements.txt exists")
    return True

def test_templates():
    """Test that required templates exist"""
    if not os.path.exists('templates/index.html'):
        print("✗ templates/index.html not found")
        return False
    
    print("✓ Required templates exist")
    return True

def main():
    """Run all deployment tests"""
    print("Running deployment readiness tests...\n")
    
    tests = [
        test_app_import,
        test_vercel_config,
        test_requirements,
        test_templates
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Deployment should work.")
        return True
    else:
        print("❌ Some tests failed. Check the issues above.")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)