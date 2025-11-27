#!/usr/bin/env python3
"""
Startup script for Bedrock Insurance Claims Processing Web Interface
"""

import os
import sys
import subprocess

def check_requirements():
    """Check if required packages are installed"""
    try:
        import flask
        import boto3
        import werkzeug
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        return False

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✓ Packages installed successfully")

def main():
    """Main startup function"""
    print("=== Bedrock Insurance Claims Processing System ===")
    print("Starting web interface...")
    
    # Change to web directory
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)
    
    # Check and install requirements
    if not check_requirements():
        install_requirements()
    
    # Start the Flask application
    print("✓ Starting Flask server on http://localhost:8000")
    print("✓ Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n✓ Server stopped by user")
    except Exception as e:
        print(f"✗ Error starting server: {e}")

if __name__ == "__main__":
    main()