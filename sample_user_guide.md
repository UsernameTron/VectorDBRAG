**RAG System User Guide**

# How to Use the Unified Agent System

## Overview
This system combines 12 specialized AI agents with a RAG (Retrieval-Augmented Generation) knowledge base for comprehensive task handling.

## Available Agents
1. **CEO Agent** - Master orchestrator for complex multi-step tasks
2. **Executor Agent** - Primary task execution with fallback models
3. **Triage Agent** - Smart routing and task analysis
4. **Research Agent** - Deep research and information synthesis
5. **Performance Agent** - Business and system performance analysis
6. **Coaching Agent** - AI-powered coaching and guidance
7. **Code Analyzer** - Advanced code analysis and review
8. **Code Debugger** - Intelligent debugging and issue detection
9. **Code Repair** - Automated code fixing and optimization
10. **Test Generator** - Automated test creation and validation
11. **Image Agent** - Visual content processing and analysis
12. **Audio Agent** - Speech and audio processing

## Key Features
- **Smart Routing**: Automatically selects the best agent for your task
- **Knowledge Base**: Upload documents to provide context to agents
- **Multi-modal**: Handles text, code, images, and audio
- **REST API**: Easy integration with web applications
- **Interactive CLI**: Simple command-line interface for quick tasks

## Quick Start Commands
```python
from agent_controller import task, upload, agents, status

# Task an agent
task("analyze this code for bugs", "debugger")

# Upload a document  
upload("my_document.txt")

# List agents
agents()

# Check status
status()
```

## API Endpoints
- `POST /api/agents/query` - Query any agent
- `POST /api/rag/upload` - Upload documents
- `GET /api/rag/status` - Check knowledge base status
- `POST /api/rag/search` - Search documents
