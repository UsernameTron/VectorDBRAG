"""
Vector Memory System for Agent Conversations and Knowledge Storage
Provides persistent memory capabilities for agents using simple text similarity.
Note: Using basic text similarity instead of embeddings for Ollama compatibility.
"""

import os
import json
import time
import pickle
import hashlib
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
from collections import Counter
import math

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """A single memory entry with vector embedding."""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: float
    agent_name: str
    entry_type: str  # conversation, knowledge, task_result, etc.
    relevance_score: Optional[float] = None

@dataclass
class ConversationTurn:
    """A single turn in a conversation."""
    role: str  # user, assistant, system
    content: str
    timestamp: float
    agent_name: Optional[str] = None

class VectorMemory:
    """Vector-based memory system for agents."""
    
    def __init__(self, memory_dir: str = "agent_memory", embedding_model: str = "text-embedding-ada-002"):
        self.memory_dir = memory_dir
        self.embedding_model = embedding_model
        self.entries: List[MemoryEntry] = []
        self.conversations: Dict[str, List[ConversationTurn]] = {}
        self.memory_file = os.path.join(memory_dir, "vector_memory.pkl")
        self.conversations_file = os.path.join(memory_dir, "conversations.json")
        
        # Create memory directory if it doesn't exist
        os.makedirs(memory_dir, exist_ok=True)
        
        # Load existing memory
        self.load_memory()
        
        logger.info(f"Vector memory initialized with {len(self.entries)} entries")
    
    def _generate_id(self, content: str, agent_name: str) -> str:
        """Generate a unique ID for a memory entry."""
        unique_str = f"{content}_{agent_name}_{time.time()}"
        return hashlib.sha256(unique_str.encode()).hexdigest()[:16]
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Get vector embedding for text."""
        try:
            response = client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536  # Ada-002 embedding dimension
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            
            dot_product = np.dot(vec1_np, vec2_np)
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    async def add_memory(self, content: str, agent_name: str, entry_type: str = "knowledge", 
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a new memory entry."""
        try:
            embedding = await self._get_embedding(content)
            entry_id = self._generate_id(content, agent_name)
            
            entry = MemoryEntry(
                id=entry_id,
                content=content,
                embedding=embedding,
                metadata=metadata or {},
                timestamp=time.time(),
                agent_name=agent_name,
                entry_type=entry_type
            )
            
            self.entries.append(entry)
            self.save_memory()
            
            logger.debug(f"Added memory entry {entry_id} for agent {agent_name}")
            return entry_id
            
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            raise
    
    async def search_memory(self, query: str, agent_name: Optional[str] = None, 
                           entry_type: Optional[str] = None, top_k: int = 5) -> List[MemoryEntry]:
        """Search memory entries by similarity."""
        try:
            query_embedding = await self._get_embedding(query)
            
            # Filter entries by agent and type if specified
            filtered_entries = self.entries
            if agent_name:
                filtered_entries = [e for e in filtered_entries if e.agent_name == agent_name]
            if entry_type:
                filtered_entries = [e for e in filtered_entries if e.entry_type == entry_type]
            
            # Calculate similarities
            for entry in filtered_entries:
                entry.relevance_score = self._cosine_similarity(query_embedding, entry.embedding)
            
            # Sort by relevance and return top k
            sorted_entries = sorted(filtered_entries, key=lambda x: x.relevance_score or 0, reverse=True)
            return sorted_entries[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return []
    
    def add_conversation_turn(self, session_id: str, role: str, content: str, agent_name: Optional[str] = None):
        """Add a turn to a conversation."""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        turn = ConversationTurn(
            role=role,
            content=content,
            timestamp=time.time(),
            agent_name=agent_name
        )
        
        self.conversations[session_id].append(turn)
        self.save_conversations()
        
        logger.debug(f"Added conversation turn for session {session_id}")
    
    def get_conversation_history(self, session_id: str, last_n: Optional[int] = None) -> List[ConversationTurn]:
        """Get conversation history for a session."""
        if session_id not in self.conversations:
            return []
        
        history = self.conversations[session_id]
        if last_n:
            return history[-last_n:]
        return history
    
    def get_agent_memories(self, agent_name: str, entry_type: Optional[str] = None) -> List[MemoryEntry]:
        """Get all memories for a specific agent."""
        memories = [e for e in self.entries if e.agent_name == agent_name]
        if entry_type:
            memories = [e for e in memories if e.entry_type == entry_type]
        return sorted(memories, key=lambda x: x.timestamp, reverse=True)
    
    def cleanup_old_memories(self, max_age_days: int = 30):
        """Remove memories older than specified days."""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        initial_count = len(self.entries)
        
        self.entries = [e for e in self.entries if e.timestamp > cutoff_time]
        
        # Also cleanup old conversations
        for session_id in list(self.conversations.keys()):
            self.conversations[session_id] = [
                turn for turn in self.conversations[session_id] 
                if turn.timestamp > cutoff_time
            ]
            if not self.conversations[session_id]:
                del self.conversations[session_id]
        
        removed_count = initial_count - len(self.entries)
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old memory entries")
            self.save_memory()
            self.save_conversations()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        agent_counts = {}
        type_counts = {}
        
        for entry in self.entries:
            agent_counts[entry.agent_name] = agent_counts.get(entry.agent_name, 0) + 1
            type_counts[entry.entry_type] = type_counts.get(entry.entry_type, 0) + 1
        
        return {
            "total_entries": len(self.entries),
            "total_conversations": len(self.conversations),
            "entries_by_agent": agent_counts,
            "entries_by_type": type_counts,
            "oldest_entry": min((e.timestamp for e in self.entries), default=0),
            "newest_entry": max((e.timestamp for e in self.entries), default=0),
            "memory_size_mb": self._estimate_memory_size()
        }
    
    def _estimate_memory_size(self) -> float:
        """Estimate memory usage in MB."""
        try:
            # Rough estimation based on typical sizes
            size_bytes = 0
            for entry in self.entries:
                size_bytes += len(entry.content.encode('utf-8'))
                size_bytes += len(entry.embedding) * 4  # 4 bytes per float
                size_bytes += len(json.dumps(entry.metadata).encode('utf-8'))
            
            return size_bytes / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0.0
    
    def save_memory(self):
        """Save memory entries to disk."""
        try:
            with open(self.memory_file, 'wb') as f:
                pickle.dump(self.entries, f)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def load_memory(self):
        """Load memory entries from disk."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'rb') as f:
                    self.entries = pickle.load(f)
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            self.entries = []
    
    def save_conversations(self):
        """Save conversations to disk."""
        try:
            # Convert ConversationTurn objects to dictionaries
            serializable_conversations = {}
            for session_id, turns in self.conversations.items():
                serializable_conversations[session_id] = [asdict(turn) for turn in turns]
            
            with open(self.conversations_file, 'w') as f:
                json.dump(serializable_conversations, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save conversations: {e}")
    
    def load_conversations(self):
        """Load conversations from disk."""
        try:
            if os.path.exists(self.conversations_file):
                with open(self.conversations_file, 'r') as f:
                    data = json.load(f)
                
                # Convert dictionaries back to ConversationTurn objects
                self.conversations = {}
                for session_id, turns in data.items():
                    self.conversations[session_id] = [
                        ConversationTurn(**turn) for turn in turns
                    ]
        except Exception as e:
            logger.error(f"Failed to load conversations: {e}")
            self.conversations = {}

# Global vector memory instance
vector_memory = VectorMemory()

# Utility functions
async def remember(content: str, agent_name: str, entry_type: str = "knowledge", 
                  metadata: Optional[Dict[str, Any]] = None) -> str:
    """Add content to agent memory."""
    return await vector_memory.add_memory(content, agent_name, entry_type, metadata)

async def recall(query: str, agent_name: Optional[str] = None, 
                entry_type: Optional[str] = None, top_k: int = 5) -> List[MemoryEntry]:
    """Search agent memory."""
    return await vector_memory.search_memory(query, agent_name, entry_type, top_k)

def add_to_conversation(session_id: str, role: str, content: str, agent_name: Optional[str] = None):
    """Add to conversation history."""
    vector_memory.add_conversation_turn(session_id, role, content, agent_name)

def get_conversation(session_id: str, last_n: Optional[int] = None) -> List[ConversationTurn]:
    """Get conversation history."""
    return vector_memory.get_conversation_history(session_id, last_n)

# Export main classes and functions
__all__ = [
    "VectorMemory",
    "MemoryEntry",
    "ConversationTurn",
    "vector_memory",
    "remember",
    "recall",
    "add_to_conversation",
    "get_conversation"
]
