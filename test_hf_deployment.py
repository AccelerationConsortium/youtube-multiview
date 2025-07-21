#!/usr/bin/env python3
"""
Test script for HF Spaces deployment readiness
"""

import os
import sys
import json

def test_hf_spaces_files():
    """Test that all required files for HF Spaces deployment exist"""
    print("Testing HF Spaces deployment readiness...")
    print("=" * 50)
    
    required_files = [
        'gradio_app.py',
        'requirements-gradio.txt', 
        'README_HF.md',
        'Dockerfile',
        '.github/workflows/deploy-hf.yml'
    ]
    
    passed = 0
    total = len(required_files)
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
            passed += 1
        else:
            print(f"✗ {file} missing")
    
    print(f"\nFile check: {passed}/{total}")
    
    # Test gradio imports
    try:
        import gradio_app
        print("✓ gradio_app.py imports successfully")
        passed += 1
        total += 1
    except Exception as e:
        print(f"✗ gradio_app.py import failed: {e}")
        total += 1
    
    # Test README_HF.md has required frontmatter
    try:
        with open('README_HF.md', 'r') as f:
            content = f.read()
            if content.startswith('---') and 'sdk: gradio' in content:
                print("✓ README_HF.md has correct HF Spaces frontmatter")
                passed += 1
            else:
                print("✗ README_HF.md missing HF Spaces frontmatter")
        total += 1
    except Exception as e:
        print(f"✗ README_HF.md validation failed: {e}")
        total += 1
    
    # Test GitHub Actions workflow
    try:
        with open('.github/workflows/deploy-hf.yml', 'r') as f:
            content = f.read()
            if 'HF_TOKEN' in content and 'huggingface.co/spaces' in content:
                print("✓ GitHub Actions workflow configured for HF Spaces")
                passed += 1
            else:
                print("✗ GitHub Actions workflow missing HF configuration")
        total += 1
    except Exception as e:
        print(f"✗ GitHub Actions workflow validation failed: {e}")
        total += 1
    
    print(f"\nTotal tests: {passed}/{total}")
    
    if passed == total:
        print("🎉 All HF Spaces deployment tests passed!")
        return True
    else:
        print("❌ Some tests failed. Check the issues above.")
        return False

def test_dual_deployment():
    """Test that both deployment options are ready"""
    print("\nTesting dual deployment readiness...")
    print("=" * 50)
    
    # Test Flask deployment files
    flask_files = ['app.py', 'requirements.txt', 'vercel.json']
    gradio_files = ['gradio_app.py', 'requirements-gradio.txt', 'README_HF.md']
    
    flask_ready = all(os.path.exists(f) for f in flask_files)
    gradio_ready = all(os.path.exists(f) for f in gradio_files)
    
    print(f"Flask (Vercel) deployment: {'✅ Ready' if flask_ready else '❌ Not ready'}")
    print(f"Gradio (HF Spaces) deployment: {'✅ Ready' if gradio_ready else '❌ Not ready'}")
    
    return flask_ready and gradio_ready

if __name__ == "__main__":
    hf_ready = test_hf_spaces_files()
    dual_ready = test_dual_deployment()
    
    if hf_ready and dual_ready:
        print("\n🚀 Ready for deployment to both platforms!")
        sys.exit(0)
    else:
        print("\n🔧 Some issues need to be resolved before deployment.")
        sys.exit(1)