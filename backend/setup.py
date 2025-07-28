#!/usr/bin/env python3
"""
Setup script for the Document Search Tool backend
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")

def install_requirements():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies")
        sys.exit(1)

def check_tesseract():
    """Check if Tesseract OCR is available"""
    try:
        subprocess.check_call(["tesseract", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✓ Tesseract OCR is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ Warning: Tesseract OCR not found. OCR functionality will be limited.")
        print("  To install Tesseract on Windows:")
        print("  1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  2. Add to PATH environment variable")

def main():
    """Main setup function"""
    print("Setting up Document Search Tool Backend...")
    print("=" * 50)
    
    check_python_version()
    install_requirements()
    check_tesseract()
    
    print("=" * 50)
    print("Setup complete!")
    print("\nNext steps:")
    print("1. Add your PDF documents to the 'documents/' directory")
    print("2. Run the backend: python app/main.py")
    print("3. Start the frontend in another terminal: npm run dev")
    print("4. Open http://localhost:5173 in your browser")

if __name__ == "__main__":
    main()
