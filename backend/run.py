#!/usr/bin/env python3
"""
Flask backend runner for the Study Snap Card application.
This script handles environment setup and runs the Flask development server.
"""

import os
import sys
from dotenv import load_dotenv

def setup_environment():
    """Load environment variables and validate configuration"""
    # Load environment variables from .env file
    load_dotenv()

    # Check for required environment variables
    required_vars = ['ANTHROPIC_API_KEY']
    missing_vars = []

    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please create a .env file with the required variables.")
        print("   You can copy .env.example and fill in your values.")
        sys.exit(1)

    print("✅ Environment variables loaded successfully")

def main():
    """Main entry point"""
    print("🚀 Starting Study Snap Card Backend...")

    # Setup environment
    setup_environment()

    # Import and run the Flask app
    try:
        from app import app
        port = app.config['FLASK_PORT']
        print(f"🌐 Backend server starting on http://localhost:{port}")
        print("📁 Make sure your .env file contains your ANTHROPIC_API_KEY")
        print("🔄 The server will auto-reload when you make changes")
        print(f"\n💡 Test the server with: curl http://localhost:{port}/health\n")

        app.run(debug=True, host='0.0.0.0', port=port)
    except ImportError as e:
        print(f"❌ Error importing Flask app: {e}")
        print("   Make sure you've installed the requirements: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()