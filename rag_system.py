"""
RAG (Retrieval-Augmented Generation) System Integration
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("ChromaDB not available. Install with: pip install chromadb")

logger = logging.getLogger(__name__)

@dataclass
class RAGResult:
    """RAG search result"""
    content: str
    source: str
    score: float
    metadata: Dict[str, Any]

class RAGSystem:
    """Enhanced RAG system with ChromaDB integration"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.initialized = False
        
    def initialize(self):
        """Initialize ChromaDB and create collection"""
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available - using mock implementation")
            self.initialized = True
            return True
            
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "RAG knowledge base for agent enhancement"}
            )
            
            self.initialized = True
            logger.info(f"✅ RAG system initialized with {self.get_document_count()} documents")
            return True
            
        except Exception as e:
            logger.error(f"❌ RAG initialization failed: {e}")
            return False
    
    def add_document(self, content: str, source: str, metadata: Dict[str, Any] = None) -> bool:
        """Add document to knowledge base"""
        try:
            if not self.initialized:
                self.initialize()
            
            if not CHROMADB_AVAILABLE or not self.collection:
                logger.warning("ChromaDB not available - document not added")
                return False
            
            # Generate embedding using ChromaDB's default embedding function
            doc_id = f"{source}_{abs(hash(content))}"
            
            self.collection.add(
                documents=[content],
                metadatas=[metadata or {"source": source}],
                ids=[doc_id]
            )
            
            logger.info(f"✅ Added document: {source}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add document {source}: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[RAGResult]:
        """Search knowledge base"""
        try:
            if not self.initialized or not self.collection or not CHROMADB_AVAILABLE:
                logger.warning("RAG system not initialized or ChromaDB not available")
                return []
            
            # Perform similarity search
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            rag_results = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 0.0
                    
                    rag_results.append(RAGResult(
                        content=doc,
                        source=metadata.get('source', 'Unknown'),
                        score=1.0 - distance,  # Convert distance to similarity score
                        metadata=metadata
                    ))
            
            logger.info(f"🔍 RAG search found {len(rag_results)} results for: {query[:50]}...")
            return rag_results
            
        except Exception as e:
            logger.error(f"❌ RAG search failed: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get RAG system status"""
        return {
            "initialized": self.initialized,
            "document_count": self.get_document_count(),
            "collection_name": "knowledge_base" if self.collection else None,
            "persist_directory": self.persist_directory,
            "chromadb_available": CHROMADB_AVAILABLE
        }
    
    def get_document_count(self) -> int:
        """Get number of documents in knowledge base"""
        try:
            if self.collection and CHROMADB_AVAILABLE:
                return self.collection.count()
            return 0
        except:
            return 0

# Global RAG instance
rag_system = RAGSystem()
