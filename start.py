#!/usr/bin/env python3
"""
Simple startup script for Resume Optimizer
Cleans cache and starts the Streamlit app
"""

import os
import shutil
import subprocess
import sys

def clean_cache():
    """Clean ChromaDB and other cache files"""
    cache_dirs = ['.chroma', 'chromadb', '__pycache__', '.streamlit/cache']

    print("🧹 Cleaning cache...")
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"   ✅ Removed {cache_dir}")
            except:
                print(f"   ⚠️  Could not remove {cache_dir}")

    # Clean output files
    if os.path.exists('output'):
        try:
            shutil.rmtree('output')
            print("   ✅ Cleaned output directory")
        except:
            pass

    print("✨ Cache cleaned!\n")

def start_app():
    """Start the Streamlit app"""
    print("🚀 Starting Resume Optimizer...")
    print("📍 App will open at: http://localhost:8501")
    print("💡 Press Ctrl+C to stop\n")

    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to start Streamlit. Make sure it's installed:")
        print("   pip install streamlit")
    except KeyboardInterrupt:
        print("\n👋 App stopped.")

if __name__ == "__main__":
    clean_cache()
    start_app()