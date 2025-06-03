"""
Knowledge Base Manager - Clean and populate with your documents
"""

import os
import shutil
from rag_system import rag_system

def reset_knowledge_base():
    """Remove all existing documents and reset knowledge base"""
    try:
        # Delete the ChromaDB directory
        if os.path.exists("./chroma_db"):
            shutil.rmtree("./chroma_db")
            print("✅ Knowledge base cleared")
        
        # Reinitialize empty knowledge base
        rag_system.initialize()
        print("✅ Fresh knowledge base created")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting knowledge base: {e}")
        return False

def add_document_from_file(file_path: str, document_type: str = "user_document"):
    """Add a document from file to knowledge base"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        filename = os.path.basename(file_path)
        success = rag_system.add_document(
            content=content,
            source=filename,
            metadata={
                "filename": filename,
                "type": document_type,
                "size": len(content),
                "path": file_path
            }
        )
        
        if success:
            print(f"✅ Added: {filename}")
        else:
            print(f"❌ Failed to add: {filename}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error adding {file_path}: {e}")
        return False

def show_knowledge_base_status():
    """Show current knowledge base status"""
    status = rag_system.get_status()
    print(f"\n📊 Knowledge Base Status:")
    print(f"   Documents: {status['document_count']}")
    print(f"   Initialized: {status['initialized']}")
    print(f"   Location: {status['persist_directory']}")
    print(f"   ChromaDB: {'Available' if status['chromadb_available'] else 'Not Available'}")

if __name__ == "__main__":
    print("🔧 Knowledge Base Manager")
    print("1. Resetting knowledge base...")
    reset_knowledge_base()
    
    print("\n2. Knowledge base ready for your documents!")
    show_knowledge_base_status()
    
    print("\n💡 Next steps:")
    print("   - Add your documents using the web interface")
    print("   - Or run: python -c 'from kb_manager import add_document_from_file; add_document_from_file(\"your_file.txt\")'")
