#!/usr/bin/env python3
"""
RAG Agent System - Quick Start Script
Simple way to get started with the unified agent system
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("🤖 RAG Agent System - Quick Start")
    print("=" * 50)
    print("🎯 12 Specialized AI Agents + Knowledge Base")
    print("📚 ChromaDB Vector Storage")
    print("🌐 REST API + Interactive CLI")
    print("=" * 50)

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import chromadb
        import flask
        import requests
        print("✅ Dependencies: All required packages installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def start_server():
    """Start the Flask server in background"""
    print("\n🚀 Starting Agent System Server...")
    try:
        # Start server in background
        server_process = subprocess.Popen([
            sys.executable, "agent_flask_integration.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give server time to start
        time.sleep(3)
        
        # Check if server is running
        import requests
        try:
            response = requests.get("http://localhost:5001/api/agents/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully on http://localhost:5001")
                return server_process
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return None
        except requests.exceptions.RequestException:
            print("❌ Server failed to start or respond")
            return None
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def show_usage():
    """Show usage options"""
    print("\n🎯 Quick Start Options:")
    print("=" * 30)
    print("1. Interactive Agent Controller")
    print("   python agent_controller.py")
    print()
    print("2. Upload Documents")
    print("   python upload_docs.py")
    print()
    print("3. Reset Knowledge Base")
    print("   python kb_manager.py")
    print()
    print("4. Python API Usage:")
    print("   from agent_controller import task, upload, agents")
    print("   task('analyze my code for bugs')")
    print("   upload('my_document.txt')")
    print("   agents()")
    print()
    print("5. REST API Endpoints:")
    print("   POST /api/agents/query")
    print("   POST /api/rag/upload")
    print("   GET  /api/rag/status")
    print()
    print("📖 Full documentation: README.md")

def quick_setup():
    """Run quick setup and demo"""
    print("\n🔧 Quick Setup:")
    
    # Check knowledge base status
    try:
        from kb_manager import show_knowledge_base_status
        show_knowledge_base_status()
    except Exception as e:
        print(f"❌ Error checking knowledge base: {e}")
    
    # Offer to upload sample documents
    print("\n📝 Sample documents available:")
    print("   - sample_user_guide.md (system overview)")
    print("   - sample_code.py (code for analysis)")
    
    choice = input("\nUpload sample documents? (y/n): ").strip().lower()
    if choice in ['y', 'yes']:
        try:
            from kb_manager import add_document_from_file
            add_document_from_file('sample_user_guide.md')
            add_document_from_file('sample_code.py')
            print("✅ Sample documents uploaded")
        except Exception as e:
            print(f"❌ Error uploading documents: {e}")

def main():
    """Main startup function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check if server is already running
    try:
        import requests
        response = requests.get("http://localhost:5001/api/agents/health", timeout=2)
        if response.status_code == 200:
            print("✅ Server already running on http://localhost:5001")
        else:
            # Start server
            server_process = start_server()
            if not server_process:
                print("❌ Failed to start server")
                return
    except requests.exceptions.RequestException:
        # Start server
        server_process = start_server()
        if not server_process:
            print("❌ Failed to start server")
            return
    except ImportError:
        print("❌ Requests package not available")
        return
    
    # Show options
    show_usage()
    
    # Quick setup option
    setup_choice = input("\nRun quick setup? (y/n): ").strip().lower()
    if setup_choice in ['y', 'yes']:
        quick_setup()
    
    print("\n🎉 RAG Agent System ready!")
    print("💡 Start with: python agent_controller.py")

if __name__ == "__main__":
    main()
