# Test script to verify the application setup
import os
import sys

print("YouTube MultiView - Setup Verification")
print("=" * 40)

# Check if we're in the right directory
current_dir = os.getcwd()
print(f"Current directory: {current_dir}")

# Check if required files exist
required_files = ['app.py', 'templates/index.html', 'static/css/style.css', 'static/js/app.js']
for file in required_files:
    if os.path.exists(file):
        print(f"✓ {file} exists")
    else:
        print(f"✗ {file} missing")

# Check if Flask is available
try:
    import flask
    print(f"✓ Flask {flask.__version__} is installed")
except ImportError:
    print("✗ Flask is not installed")
    print("Run: pip install flask")

print("\nTo start the application:")
print("1. Open terminal/command prompt")
print("2. Navigate to this directory")
print("3. Run: python app.py")
print("4. Open browser to: http://localhost:5000")
