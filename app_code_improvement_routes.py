"""
Code Improvement API Routes
Flask routes for RAG-enhanced code analysis and improvement
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, current_app
from functools import wraps

from unified_agent_system_rag_integration import CodeImprovementOrchestrator


def create_code_improvement_blueprint() -> Blueprint:
    """Create and configure the code improvement blueprint."""
    bp = Blueprint('code_improvement', __name__, url_prefix='/api/code')
    
    def require_orchestrator(f):
        """Decorator to ensure code improvement orchestrator is available."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(current_app, 'code_orchestrator') or current_app.code_orchestrator is None:
                return jsonify({
                    "success": False,
                    "error": "Code improvement system not available",
                    "message": "RAG-Agent integration not initialized"
                }), 503
            return f(*args, **kwargs)
        return decorated_function
    
    def async_route(f):
        """Decorator to handle async routes."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return asyncio.run(f(*args, **kwargs))
        return decorated_function
    
    @bp.route('/analyze', methods=['POST'])
    @require_orchestrator
    @async_route
    async def analyze_code():
        """
        Analyze code using RAG-enhanced agents.
        
        Request JSON:
        {
            "code": "string - code to analyze",
            "analysis_type": "string - general|performance|security|testing|debugging (optional)",
            "context": "object - additional context (optional)"
        }
        
        Response JSON:
        {
            "success": true|false,
            "analysis_type": "string",
            "agent_used": "string",
            "result": "string - analysis result",
            "execution_time": number,
            "timestamp": number,
            "error": "string (if success=false)"
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "success": False,
                    "error": "No JSON data provided"
                }), 400
            
            code = data.get('code', '').strip()
            if not code:
                return jsonify({
                    "success": False,
                    "error": "Code parameter is required"
                }), 400
            
            analysis_type = data.get('analysis_type', 'general')
            context = data.get('context', {})
            
            # Validate analysis type
            valid_types = ['general', 'performance', 'security', 'testing', 'debugging']
            if analysis_type not in valid_types:
                return jsonify({
                    "success": False,
                    "error": f"Invalid analysis_type. Must be one of: {', '.join(valid_types)}"
                }), 400
            
            # Perform code analysis
            orchestrator = current_app.code_orchestrator
            result = await orchestrator.analyze_code(code, analysis_type, context)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }), 500
    
    @bp.route('/improve', methods=['POST'])
    @require_orchestrator
    @async_route
    async def improve_code():
        """
        Improve code using RAG-enhanced agents.
        
        Request JSON:
        {
            "code": "string - code to improve",
            "improvement_type": "string - general|performance|debugging|repair (optional)",
            "context": "object - additional context (optional)"
        }
        
        Response JSON:
        {
            "success": true|false,
            "improvement_type": "string",
            "agent_used": "string",
            "result": "string - improvement suggestions",
            "execution_time": number,
            "timestamp": number,
            "error": "string (if success=false)"
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "success": False,
                    "error": "No JSON data provided"
                }), 400
            
            code = data.get('code', '').strip()
            if not code:
                return jsonify({
                    "success": False,
                    "error": "Code parameter is required"
                }), 400
            
            improvement_type = data.get('improvement_type', 'general')
            context = data.get('context', {})
            
            # Validate improvement type
            valid_types = ['general', 'performance', 'debugging', 'repair']
            if improvement_type not in valid_types:
                return jsonify({
                    "success": False,
                    "error": f"Invalid improvement_type. Must be one of: {', '.join(valid_types)}"
                }), 400
            
            # Perform code improvement
            orchestrator = current_app.code_orchestrator
            result = await orchestrator.improve_code(code, improvement_type, context)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }), 500
    
    @bp.route('/rag-query', methods=['POST'])
    @require_orchestrator
    @async_route
    async def rag_query():
        """
        Query coding knowledge using RAG-enhanced research agent.
        
        Request JSON:
        {
            "query": "string - knowledge query",
            "context": "object - additional context (optional)"
        }
        
        Response JSON:
        {
            "success": true|false,
            "query": "string",
            "agent_used": "string",
            "result": "string - knowledge response",
            "execution_time": number,
            "timestamp": number,
            "error": "string (if success=false)"
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "success": False,
                    "error": "No JSON data provided"
                }), 400
            
            query = data.get('query', '').strip()
            if not query:
                return jsonify({
                    "success": False,
                    "error": "Query parameter is required"
                }), 400
            
            context = data.get('context', {})
            
            # Perform knowledge query
            orchestrator = current_app.code_orchestrator
            result = await orchestrator.query_coding_knowledge(query, context)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }), 500
    
    @bp.route('/agents/status', methods=['GET'])
    @require_orchestrator
    def agent_status():
        """
        Get status of code improvement agents.
        
        Response JSON:
        {
            "total_rag_enhanced_agents": number,
            "rag_system_available": boolean,
            "agents": {
                "agent_type": {
                    "name": "string",
                    "base_agent": "string",
                    "specializations": ["string"],
                    "status": "string"
                }
            }
        }
        """
        try:
            orchestrator = current_app.code_orchestrator
            status = orchestrator.get_agent_status()
            return jsonify(status)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }), 500
    
    @bp.route('/health', methods=['GET'])
    def health_check():
        """
        Health check for code improvement system.
        
        Response JSON:
        {
            "status": "healthy|degraded|unavailable",
            "rag_system": boolean,
            "agent_system": boolean,
            "orchestrator": boolean,
            "message": "string"
        }
        """
        try:
            has_orchestrator = hasattr(current_app, 'code_orchestrator') and current_app.code_orchestrator is not None
            has_rag = hasattr(current_app, 'search_system') and current_app.search_system is not None
            has_agents = hasattr(current_app, 'agent_manager') and current_app.agent_manager is not None
            
            if has_orchestrator and has_rag and has_agents:
                status = "healthy"
                message = "All code improvement systems operational"
            elif has_rag and has_agents:
                status = "degraded"
                message = "RAG and agents available but not integrated"
            else:
                status = "unavailable"
                message = "Code improvement systems not available"
            
            return jsonify({
                "status": status,
                "rag_system": has_rag,
                "agent_system": has_agents,
                "orchestrator": has_orchestrator,
                "message": message,
                "timestamp": time.time()
            })
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }), 500
    
    @bp.route('/examples', methods=['GET'])
    def get_examples():
        """
        Get code improvement examples for different types.
        
        Response JSON:
        {
            "analysis_examples": {...},
            "improvement_examples": {...},
            "query_examples": [...]
        }
        """
        examples = {
            "analysis_examples": {
                "general": {
                    "description": "General code analysis for quality and structure",
                    "sample_code": "def calculate_total(items):\n    total = 0\n    for item in items:\n        total += item['price']\n    return total",
                    "expected_analysis": "Code structure, readability, error handling, optimization opportunities"
                },
                "performance": {
                    "description": "Performance-focused code analysis",
                    "sample_code": "result = []\nfor i in range(1000000):\n    result.append(i * 2)",
                    "expected_analysis": "Memory usage, algorithmic complexity, performance bottlenecks"
                },
                "security": {
                    "description": "Security-focused code analysis",
                    "sample_code": "user_input = request.args.get('query')\nresult = db.execute(f'SELECT * FROM users WHERE name = {user_input}')",
                    "expected_analysis": "SQL injection vulnerabilities, input validation, security best practices"
                }
            },
            "improvement_examples": {
                "general": {
                    "description": "General code improvements",
                    "focus": "Code quality, readability, maintainability"
                },
                "performance": {
                    "description": "Performance optimizations",
                    "focus": "Speed, memory usage, algorithmic efficiency"
                },
                "debugging": {
                    "description": "Debugging assistance",
                    "focus": "Error identification, troubleshooting, diagnostic techniques"
                },
                "repair": {
                    "description": "Code repair suggestions",
                    "focus": "Bug fixes, error correction, code stability"
                }
            },
            "query_examples": [
                "What are the best practices for error handling in Python?",
                "How do I optimize database queries for better performance?",
                "What security considerations should I have for web APIs?",
                "How do I implement proper logging in a Flask application?",
                "What testing strategies work best for microservices?",
                "How do I handle memory management in large-scale applications?"
            ]
        }
        
        return jsonify(examples)
    
    return bp


def register_code_improvement_routes(app):
    """Register code improvement routes with the Flask app."""
    bp = create_code_improvement_blueprint()
    app.register_blueprint(bp)
    print("✅ Code improvement API routes registered")


# Export main functions
__all__ = ['create_code_improvement_blueprint', 'register_code_improvement_routes']
