#!/usr/bin/env python3
"""
Simple script to run the Streamlit app
"""
import subprocess
import sys
import os

def main():
    """Run the Streamlit app"""
    try:
        # Ensure we're in the right directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run streamlit with proper configuration
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.maxUploadSize", "200",
            "--server.maxMessageSize", "200"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down Streamlit app...")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")

if __name__ == "__main__":
    main()