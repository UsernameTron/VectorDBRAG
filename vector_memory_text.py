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
    """A single memory entry with text similarity support."""
    id: str
    content: str
    keywords: List[str]  # Instead of embeddings, use keywords
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

class TextSimilarityMemory:
    """Text similarity-based memory system for agents."""
    
    def __init__(self, memory_dir: str = "agent_memory"):
        self.memory_dir = memory_dir
        self.entries: List[MemoryEntry] = []
        self.conversations: Dict[str, List[ConversationTurn]] = {}
        self.memory_file = os.path.join(memory_dir, "text_memory.pkl")
        self.conversations_file = os.path.join(memory_dir, "conversations.json")
        
        # Create memory directory if it doesn't exist
        os.makedirs(memory_dir, exist_ok=True)
        
        # Load existing memory
        self.load_memory()
        
        logger.info(f"Text similarity memory initialized with {len(self.entries)} entries")
    
    def _generate_id(self, content: str, agent_name: str) -> str:
        """Generate a unique ID for a memory entry."""
        unique_str = f"{content}_{agent_name}_{time.time()}"
        return hashlib.sha256(unique_str.encode()).hexdigest()[:16]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for similarity matching."""
        # Simple keyword extraction
        text = text.lower()
        # Remove punctuation and split into words
        words = re.findall(r'\b\w+\b', text)
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'under', 'over', 'is', 'was', 'are', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Return most common keywords (up to 20)
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(20)]
    
    def _calculate_similarity(self, keywords1: List[str], keywords2: List[str]) -> float:
        """Calculate similarity between two keyword lists using Jaccard similarity."""
        if not keywords1 or not keywords2:
            return 0.0
        
        set1 = set(keywords1)
        set2 = set(keywords2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _calculate_tfidf_similarity(self, text1: str, text2: str) -> float:
        """Calculate TF-IDF based similarity between two texts."""
        words1 = re.findall(r'\b\w+\b', text1.lower())
        words2 = re.findall(r'\b\w+\b', text2.lower())
        
        # Create vocabulary
        vocab = set(words1 + words2)
        
        if not vocab:
            return 0.0
        
        # Calculate TF for each document
        tf1 = Counter(words1)
        tf2 = Counter(words2)
        
        # Calculate cosine similarity
        dot_product = sum(tf1[word] * tf2[word] for word in vocab)
        
        norm1 = math.sqrt(sum(tf1[word] ** 2 for word in vocab))
        norm2 = math.sqrt(sum(tf2[word] ** 2 for word in vocab))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def add_memory(self, content: str, agent_name: str, entry_type: str = "knowledge", 
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a new memory entry."""
        try:
            keywords = self._extract_keywords(content)
            entry_id = self._generate_id(content, agent_name)
            
            entry = MemoryEntry(
                id=entry_id,
                content=content,
                keywords=keywords,
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
            query_keywords = self._extract_keywords(query)
            
            # Filter entries by agent and type if specified
            filtered_entries = self.entries
            if agent_name:
                filtered_entries = [e for e in filtered_entries if e.agent_name == agent_name]
            if entry_type:
                filtered_entries = [e for e in filtered_entries if e.entry_type == entry_type]
            
            # Calculate similarities
            for entry in filtered_entries:
                # Combine keyword similarity and TF-IDF similarity
                keyword_sim = self._calculate_similarity(query_keywords, entry.keywords)
                tfidf_sim = self._calculate_tfidf_similarity(query, entry.content)
                
                # Weighted combination (70% TF-IDF, 30% keywords)
                entry.relevance_score = 0.7 * tfidf_sim + 0.3 * keyword_sim
            
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
            "memory_type": "text_similarity"
        }
    
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

# Create a compatibility alias for the VectorMemory class
VectorMemory = TextSimilarityMemory

# Global memory instance
vector_memory = TextSimilarityMemory()

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
    "TextSimilarityMemory",
    "MemoryEntry",
    "ConversationTurn",
    "vector_memory",
    "remember",
    "recall",
    "add_to_conversation",
    "get_conversation"
]
