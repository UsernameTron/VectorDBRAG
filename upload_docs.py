"""
Document Upload Utility - Easy way to add your documents to the knowledge base
"""

import os
import glob
from pathlib import Path
from kb_manager import add_document_from_file, show_knowledge_base_status, reset_knowledge_base

def upload_folder(folder_path: str, file_patterns: list = None):
    """Upload all files from a folder matching patterns"""
    if file_patterns is None:
        file_patterns = ["*.txt", "*.md", "*.py", "*.js", "*.html", "*.css", "*.json", "*.yaml", "*.yml"]
    
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ Folder not found: {folder_path}")
        return False
    
    print(f"📁 Uploading from: {folder_path}")
    uploaded = 0
    
    for pattern in file_patterns:
        files = glob.glob(str(folder / pattern), recursive=True)
        for file_path in files:
            if os.path.isfile(file_path):
                if add_document_from_file(file_path):
                    uploaded += 1
    
    print(f"✅ Uploaded {uploaded} documents")
    return uploaded > 0

def upload_files(file_paths: list):
    """Upload specific files to knowledge base"""
    uploaded = 0
    for file_path in file_paths:
        if os.path.isfile(file_path):
            if add_document_from_file(file_path):
                uploaded += 1
        else:
            print(f"❌ File not found: {file_path}")
    
    print(f"✅ Uploaded {uploaded} documents")
    return uploaded > 0

def interactive_upload():
    """Interactive document upload"""
    print("🚀 Interactive Document Upload")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Upload a single file")
        print("2. Upload all files from a folder")
        print("3. Reset knowledge base (clear all)")
        print("4. Show knowledge base status")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            file_path = input("Enter file path: ").strip()
            if file_path:
                add_document_from_file(file_path)
        
        elif choice == "2":
            folder_path = input("Enter folder path: ").strip()
            if folder_path:
                upload_folder(folder_path)
        
        elif choice == "3":
            confirm = input("⚠️  This will delete ALL documents. Continue? (yes/no): ").strip().lower()
            if confirm in ["yes", "y"]:
                reset_knowledge_base()
        
        elif choice == "4":
            show_knowledge_base_status()
        
        elif choice == "5":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    interactive_upload()
