# Local AI Integration - Technical Implementation Guide
## Code Structure and Implementation Details

### Overview
This document provides the technical implementation details for integrating local AI capabilities into our Business Intelligence & Knowledge Management Platform.

---

## File Structure for Integration

```
RAG/
├── app.py (enhanced)
├── config.py (enhanced with hybrid configuration)
├── search_system.py (enhanced with routing)
├── local_ai/
│   ├── __init__.py
│   ├── agents.py (from 01-Local-Advanced-Model)
│   ├── config.py (local AI configuration)
│   ├── vector_memory.py (FAISS integration)
│   ├── orchestrator.py (query routing)
│   └── complexity_analyzer.py (new)
├── integrations/
│   ├── analytics_integration.py (existing)
│   ├── report_ingestion.py (existing)
│   └── hybrid_ai_integration.py (new)
├── templates/
│   ├── analytics.html (existing)
│   └── local_ai_dashboard.html (new)
└── requirements.txt (enhanced)
```

---

## Implementation Steps

### Step 1: Enhanced Requirements
```bash
# Add to requirements.txt
ollama
faiss-cpu
transformers
torch
streamlit
sentence-transformers
numpy
scikit-learn
```

### Step 2: Hybrid Configuration System
```python
# Enhanced config.py
import os
from typing import Dict, Any

class HybridConfig:
    def __init__(self, environment: str = 'development'):
        # Existing OpenAI configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # Local AI configuration
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.local_model_name = os.getenv('LOCAL_MODEL', 'phi3.5')
        self.local_embedding_model = os.getenv('LOCAL_EMBEDDING_MODEL', 'nomic-embed-text')
        
        # Routing configuration
        self.complexity_threshold = float(os.getenv('COMPLEXITY_THRESHOLD', '0.7'))
        self.local_ai_ratio = float(os.getenv('LOCAL_AI_RATIO', '0.8'))
        self.enable_fallback = os.getenv('ENABLE_FALLBACK', 'true').lower() == 'true'
        self.max_local_tokens = int(os.getenv('MAX_LOCAL_TOKENS', '4096'))
        
        # Performance settings
        self.local_timeout = int(os.getenv('LOCAL_TIMEOUT', '30'))
        self.cloud_timeout = int(os.getenv('CLOUD_TIMEOUT', '60'))
        self.enable_caching = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
        
        # Vector store configuration
        self.faiss_index_path = os.getenv('FAISS_INDEX_PATH', './data/faiss_index')
        self.hybrid_search_ratio = float(os.getenv('HYBRID_SEARCH_RATIO', '0.7'))

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
```

### Step 3: Query Complexity Analyzer
```python
# local_ai/complexity_analyzer.py
import re
import numpy as np
from typing import Dict, List, Tuple
from transformers import AutoTokenizer

class ComplexityAnalyzer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-medium')
        
        # Complexity indicators
        self.complex_patterns = [
            r'\b(analyze|synthesize|compare|contrast|evaluate)\b',
            r'\b(complex|complicated|intricate|sophisticated)\b',
            r'\b(multiple|various|several|numerous)\b.*\b(factors|aspects|elements)\b',
            r'\b(relationship|correlation|causation|dependency)\b',
            r'\b(strategy|strategic|framework|methodology)\b'
        ]
        
        self.simple_patterns = [
            r'\b(what|when|where|who|how many)\b',
            r'\b(list|show|display|find)\b',
            r'\b(simple|basic|quick|direct)\b'
        ]

    def analyze(self, query: str, context: str = None) -> float:
        """
        Analyze query complexity and return score (0.0 to 1.0).
        0.0 = simple, 1.0 = complex
        """
        complexity_score = 0.0
        
        # Token count analysis
        tokens = self.tokenizer.encode(query)
        token_complexity = min(len(tokens) / 100, 0.3)  # Cap at 0.3
        complexity_score += token_complexity
        
        # Pattern matching
        complex_matches = sum(1 for pattern in self.complex_patterns 
                            if re.search(pattern, query.lower()))
        simple_matches = sum(1 for pattern in self.simple_patterns 
                           if re.search(pattern, query.lower()))
        
        pattern_complexity = (complex_matches * 0.2) - (simple_matches * 0.1)
        complexity_score += max(0, pattern_complexity)
        
        # Question structure analysis
        question_words = ['what', 'how', 'why', 'when', 'where', 'who']
        if any(word in query.lower() for word in question_words):
            if 'why' in query.lower() or 'how' in query.lower():
                complexity_score += 0.2
            else:
                complexity_score += 0.1
        
        # Context dependency
        if context:
            context_tokens = self.tokenizer.encode(context)
            if len(context_tokens) > 500:
                complexity_score += 0.15
        
        return min(complexity_score, 1.0)
```

### Step 4: Hybrid Agent System
```python
# local_ai/hybrid_agents.py
import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import ollama
import openai
from .complexity_analyzer import ComplexityAnalyzer

class LocalAgent:
    def __init__(self, config):
        self.config = config
        self.client = ollama.Client(host=config.ollama_base_url)
        self.model_name = config.local_model_name
        
    async def process(self, query: str, context: str = None) -> Dict[str, Any]:
        """Process query using local Ollama model."""
        try:
            start_time = time.time()
            
            # Prepare prompt
            prompt = self._prepare_prompt(query, context)
            
            # Generate response
            response = await asyncio.to_thread(
                self.client.generate,
                model=self.model_name,
                prompt=prompt,
                options={'temperature': 0.7, 'top_p': 0.9}
            )
            
            processing_time = time.time() - start_time
            
            return {
                'response': response['response'],
                'model': f'local:{self.model_name}',
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat(),
                'source': 'local_ai'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'model': f'local:{self.model_name}',
                'source': 'local_ai',
                'timestamp': datetime.now().isoformat()
            }
    
    def _prepare_prompt(self, query: str, context: str = None) -> str:
        """Prepare optimized prompt for local model."""
        base_prompt = f"Query: {query}\n\n"
        
        if context:
            base_prompt += f"Context: {context}\n\n"
        
        base_prompt += "Response:"
        return base_prompt

class CloudAgent:
    def __init__(self, config):
        self.config = config
        self.client = openai.OpenAI(api_key=config.openai_api_key)
        self.model_name = config.openai_model
        
    async def process(self, query: str, context: str = None) -> Dict[str, Any]:
        """Process query using OpenAI model."""
        try:
            start_time = time.time()
            
            messages = self._prepare_messages(query, context)
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model_name,
                messages=messages,
                temperature=0.7
            )
            
            processing_time = time.time() - start_time
            
            return {
                'response': response.choices[0].message.content,
                'model': f'cloud:{self.model_name}',
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat(),
                'source': 'cloud_ai',
                'usage': response.usage.dict() if response.usage else None
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'model': f'cloud:{self.model_name}',
                'source': 'cloud_ai',
                'timestamp': datetime.now().isoformat()
            }
    
    def _prepare_messages(self, query: str, context: str = None) -> List[Dict[str, str]]:
        """Prepare messages for OpenAI API."""
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant for business intelligence and knowledge management."}
        ]
        
        if context:
            messages.append({
                "role": "user", 
                "content": f"Context: {context}\n\nQuery: {query}"
            })
        else:
            messages.append({"role": "user", "content": query})
        
        return messages

class HybridAgentSystem:
    def __init__(self, config):
        self.config = config
        self.local_agent = LocalAgent(config)
        self.cloud_agent = CloudAgent(config)
        self.complexity_analyzer = ComplexityAnalyzer()
        
        # Performance tracking
        self.stats = {
            'local_queries': 0,
            'cloud_queries': 0,
            'fallback_uses': 0,
            'total_processing_time': 0.0
        }
    
    async def process_query(self, query: str, context: str = None, force_local: bool = False) -> Dict[str, Any]:
        """Main query processing with intelligent routing."""
        
        # Analyze complexity
        complexity_score = self.complexity_analyzer.analyze(query, context)
        
        # Routing decision
        use_local = (
            force_local or 
            complexity_score < self.config.complexity_threshold
        )
        
        if use_local:
            result = await self._process_with_local(query, context)
            self.stats['local_queries'] += 1
        else:
            result = await self._process_with_cloud(query, context)
            self.stats['cloud_queries'] += 1
        
        # Add routing information
        result['complexity_score'] = complexity_score
        result['routing_decision'] = 'local' if use_local else 'cloud'
        
        return result
    
    async def _process_with_local(self, query: str, context: str = None) -> Dict[str, Any]:
        """Process with local AI, fallback to cloud if needed."""
        result = await self.local_agent.process(query, context)
        
        # Check if fallback is needed
        if 'error' in result and self.config.enable_fallback:
            self.stats['fallback_uses'] += 1
            result = await self.cloud_agent.process(query, context)
            result['fallback_used'] = True
        
        return result
    
    async def _process_with_cloud(self, query: str, context: str = None) -> Dict[str, Any]:
        """Process with cloud AI."""
        return await self.cloud_agent.process(query, context)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        total_queries = self.stats['local_queries'] + self.stats['cloud_queries']
        
        return {
            'total_queries': total_queries,
            'local_ratio': self.stats['local_queries'] / max(total_queries, 1),
            'cloud_ratio': self.stats['cloud_queries'] / max(total_queries, 1),
            'fallback_rate': self.stats['fallback_uses'] / max(self.stats['local_queries'], 1),
            'stats': self.stats
        }
```

### Step 5: Enhanced Search System Integration
```python
# Enhanced search_system.py additions
from local_ai.hybrid_agents import HybridAgentSystem

class EnhancedSearchSystem:
    def __init__(self, config):
        # Existing initialization
        self.config = config
        self.vector_stores = {}
        
        # Add hybrid AI system
        self.hybrid_ai = HybridAgentSystem(config)
        
        # Add FAISS integration
        self.faiss_enabled = config.enable_faiss if hasattr(config, 'enable_faiss') else False
    
    async def hybrid_search(self, query: str, store_id: str = None, use_local_ai: bool = None) -> Dict[str, Any]:
        """Enhanced search with local AI capabilities."""
        
        # Get relevant documents
        search_results = await self.search_documents(query, store_id)
        
        # Prepare context from search results
        context = self._prepare_context_from_results(search_results)
        
        # Process with hybrid AI
        ai_response = await self.hybrid_ai.process_query(
            query, 
            context, 
            force_local=use_local_ai
        )
        
        return {
            'query': query,
            'search_results': search_results,
            'ai_response': ai_response,
            'timestamp': datetime.now().isoformat()
        }
    
    def _prepare_context_from_results(self, search_results: List[Dict]) -> str:
        """Prepare context string from search results."""
        context_parts = []
        
        for result in search_results[:5]:  # Use top 5 results
            if 'content' in result:
                context_parts.append(result['content'][:500])  # Limit content length
        
        return '\n\n'.join(context_parts)
```

### Step 6: API Endpoint Enhancements
```python
# Additional routes for app.py

@app.route('/api/hybrid-search', methods=['POST'])
def hybrid_search():
    """Enhanced search endpoint with local AI capabilities."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        store_id = data.get('store_id')
        use_local_ai = data.get('use_local_ai')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Use async wrapper for hybrid search
        result = asyncio.run(
            current_app.search_system.hybrid_search(query, store_id, use_local_ai)
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Search failed',
            'message': str(e)
        }), 500

@app.route('/api/local-ai/stats')
def local_ai_stats():
    """Get local AI performance statistics."""
    try:
        stats = current_app.search_system.hybrid_ai.get_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to get stats',
            'message': str(e)
        }), 500

@app.route('/api/local-ai/config')
def local_ai_config():
    """Get local AI configuration."""
    try:
        config_data = {
            'local_model': current_app.config.get('local_model_name'),
            'complexity_threshold': current_app.config.get('complexity_threshold'),
            'local_ai_ratio': current_app.config.get('local_ai_ratio'),
            'ollama_url': current_app.config.get('ollama_base_url')
        }
        return jsonify({
            'success': True,
            'data': config_data
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to get config',
            'message': str(e)
        }), 500
```

---

## Installation and Setup Commands

### 1. Install Ollama
```bash
# macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull required model
ollama pull phi3.5
ollama pull nomic-embed-text
```

### 2. Install Python Dependencies
```bash
cd /Users/cpconnor/projects/RAG
pip install ollama faiss-cpu transformers torch streamlit sentence-transformers
```

### 3. Environment Configuration
```bash
# Add to .env file
OLLAMA_BASE_URL=http://localhost:11434
LOCAL_MODEL=phi3.5
LOCAL_EMBEDDING_MODEL=nomic-embed-text
COMPLEXITY_THRESHOLD=0.7
LOCAL_AI_RATIO=0.8
ENABLE_FALLBACK=true
ENABLE_CACHING=true
FAISS_INDEX_PATH=./data/faiss_index
```

### 4. Test Local AI Setup
```bash
# Test Ollama connection
curl http://localhost:11434/api/generate -d '{
  "model": "phi3.5",
  "prompt": "Hello, how are you?",
  "stream": false
}'
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_hybrid_ai.py
import pytest
import asyncio
from local_ai.hybrid_agents import HybridAgentSystem
from local_ai.complexity_analyzer import ComplexityAnalyzer

class TestComplexityAnalyzer:
    def test_simple_query(self):
        analyzer = ComplexityAnalyzer()
        score = analyzer.analyze("What is the weather today?")
        assert score < 0.5
    
    def test_complex_query(self):
        analyzer = ComplexityAnalyzer()
        score = analyzer.analyze("Analyze the complex relationship between customer satisfaction and revenue trends across multiple business units")
        assert score > 0.5

class TestHybridAgentSystem:
    @pytest.mark.asyncio
    async def test_local_agent_simple_query(self):
        # Test with mock configuration
        pass
    
    @pytest.mark.asyncio
    async def test_routing_decision(self):
        # Test query routing logic
        pass
```

### Integration Tests
```python
# tests/test_integration.py
import requests

def test_hybrid_search_endpoint():
    response = requests.post('http://localhost:5001/api/hybrid-search', 
                           json={'query': 'test query'})
    assert response.status_code == 200
    data = response.json()
    assert 'ai_response' in data['data']

def test_local_ai_stats():
    response = requests.get('http://localhost:5001/api/local-ai/stats')
    assert response.status_code == 200
```

---

## Monitoring and Metrics

### Key Metrics to Track
1. **Query Routing Ratio**: Local vs Cloud processing
2. **Response Times**: Local vs Cloud performance
3. **Fallback Rate**: How often local AI fails and falls back
4. **Cost Savings**: Actual reduction in OpenAI API usage
5. **User Satisfaction**: Quality of local AI responses

### Dashboard Enhancements
```javascript
// static/js/local_ai_dashboard.js
class LocalAIDashboard {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.init();
    }
    
    async init() {
        await this.loadStats();
        setInterval(() => this.loadStats(), this.updateInterval);
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/local-ai/stats');
            const data = await response.json();
            this.updateCharts(data.data);
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }
    
    updateCharts(stats) {
        // Update routing ratio chart
        this.updateRoutingChart(stats);
        
        // Update performance metrics
        this.updatePerformanceMetrics(stats);
        
        // Update cost savings
        this.updateCostSavings(stats);
    }
}
```

---

## Deployment Checklist

### Pre-deployment
- [ ] Ollama installed and running
- [ ] Required models downloaded (phi3.5, nomic-embed-text)
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Unit tests passing
- [ ] Integration tests passing

### Deployment
- [ ] Backup existing system
- [ ] Deploy new code
- [ ] Restart services
- [ ] Verify all endpoints
- [ ] Monitor performance metrics
- [ ] Validate query routing

### Post-deployment
- [ ] Monitor system performance
- [ ] Track cost savings
- [ ] Collect user feedback
- [ ] Optimize routing thresholds
- [ ] Document lessons learned

---

This technical implementation guide provides the complete roadmap for integrating local AI capabilities. The next step would be to begin the implementation process starting with the infrastructure setup and dependency installation.
