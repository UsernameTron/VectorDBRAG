"""
Enhanced Agent Integration for VectorDBRAG
Integrates the shared agent framework with VectorDBRAG's Flask routes
Replaces the original agent system with the enhanced factory
"""

import os
import json
import time
import asyncio
from typing import Dict, Any, List, Optional, Union
from flask import Flask, request, jsonify, render_template, g, current_app
from functools import wraps

from shared_agents.core.agent_factory import AgentCapability, AgentResponse
from agents.enhanced.factory import EnhancedAgentFactory, default_factory


# Create a global factory instance for use across the application
_factory_instance = None

def get_factory():
    """Get or create the global factory instance."""
    global _factory_instance
    if _factory_instance is None:
        config = {
            # Basic configuration for all agents
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'default_model': 'gpt-4o',
            'fast_model': 'gpt-4o-mini',
        }
        
        # Try to get RAG system and analytics from app context
        try:
            if hasattr(current_app, 'search_system'):
                config['rag_system'] = current_app.search_system
            
            if hasattr(current_app, 'analytics_integration'):
                config['analytics'] = current_app.analytics_integration
        except RuntimeError:
            # Flask app context not available
            pass
            
        _factory_instance = EnhancedAgentFactory(config)
    
    return _factory_instance


class EnhancedAgentIntegration:
    """
    Integration layer between VectorDBRAG Flask app and enhanced agent factory.
    Handles routing of agent requests to appropriate agents using the shared framework.
    """
    
    def __init__(self, app: Flask):
        """
        Initialize enhanced agent integration.
        
        Args:
            app: Flask application
        """
        self.app = app
    
    def register_routes(self):
        """Register enhanced agent routes with the Flask app."""
        app = self.app
        
        def agent_error_handler(f):
            """Decorator for consistent agent error handling."""
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    return jsonify({
                        'error': 'Enhanced agent processing failed',
                        'message': str(e),
                        'agent_system': 'enhanced_framework'
                    }), 500
            return decorated_function
        
        # Enhanced Agent Routes
        
        @app.route('/enhanced/agents')
        def enhanced_agents_dashboard():
            """Render the enhanced agents dashboard page."""
            return render_template('enhanced_agents.html')
        
        @app.route('/api/enhanced/agents/query', methods=['POST'])
        @agent_error_handler
        def enhanced_agent_query():
            """Process a query through an enhanced agent."""
            data = request.get_json()
            if not data or 'query' not in data:
                return jsonify({'error': 'Query is required'}), 400
            
            query = data['query']
            context = data.get('context', {})
            agent_type = data.get('agent_type', 'code_analysis')
            
            # Add request metadata to context
            context.update({
                'request_id': f"req_{int(time.time() * 1000)}",
                'timestamp': time.time(),
                'user_agent': request.headers.get('User-Agent', ''),
                'ip_address': request.remote_addr
            })
            
            # Create input data for agent
            input_data = {
                'content': query,
                'query': query,
                'context': context
            }
            
            # Create and execute agent
            try:
                # Get factory instance
                factory = get_factory()
                
                # Create agent
                agent = factory.create_agent(agent_type)
                
                # Execute agent asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(agent._safe_execute(input_data))
                finally:
                    loop.close()
                
                return jsonify({
                    'status': 'success',
                    'response': {
                        'task_id': f"task_{int(time.time() * 1000)}",
                        'agent_name': agent.name,
                        'agent_type': agent.agent_type,
                        'result': response.result,
                        'success': response.success,
                        'execution_time': response.execution_time,
                        'metadata': response.metadata or {},
                        'error': response.error
                    }
                })
                
            except Exception as e:
                return jsonify({'error': f'Enhanced agent query failed: {str(e)}'}), 400
        
        @app.route('/api/enhanced/agents/capability', methods=['POST'])
        @agent_error_handler
        def enhanced_agent_by_capability():
            """Process a query using an agent with a specific capability."""
            data = request.get_json()
            if not data or 'capability' not in data:
                return jsonify({'error': 'Capability is required'}), 400
            
            capability_name = data['capability']
            input_data = data.get('input_data', {})
            
            # Map capability string to enum
            try:
                capability = AgentCapability(capability_name)
            except ValueError:
                return jsonify({'error': f'Unknown capability: {capability_name}'}), 400
            
            # Create agent by capability
            try:
                # Get factory instance
                factory = get_factory()
                
                # Create agent by capability
                agent = factory.create_agent_by_capability(capability)
                
                # Execute agent asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(agent._safe_execute(input_data))
                finally:
                    loop.close()
                
                return jsonify({
                    'status': 'success',
                    'response': {
                        'task_id': f"task_{int(time.time() * 1000)}",
                        'agent_name': agent.name,
                        'agent_type': agent.agent_type,
                        'capability': capability_name,
                        'result': response.result,
                        'success': response.success,
                        'execution_time': response.execution_time,
                        'metadata': response.metadata or {},
                        'error': response.error
                    }
                })
                
            except Exception as e:
                return jsonify({'error': f'Enhanced capability query failed: {str(e)}'}), 400
        
        @app.route('/api/enhanced/agents/types', methods=['GET'])
        @agent_error_handler
        def get_agent_types():
            """Get all available agent types."""
            factory = get_factory()
            agent_types = factory.get_agent_types()
            return jsonify({
                'status': 'success',
                'agent_types': agent_types
            })
        
        @app.route('/api/enhanced/agents/capabilities', methods=['GET'])
        @agent_error_handler
        def get_agent_capabilities():
            """Get all available agent capabilities."""
            capabilities = [capability.value for capability in AgentCapability]
            return jsonify({
                'status': 'success',
                'capabilities': capabilities
            })
        
        @app.route('/api/enhanced/agents/status', methods=['GET'])
        @agent_error_handler
        def get_enhanced_agent_status():
            """Get status of the enhanced agent system."""
            factory = get_factory()
            
            # Get factory status
            factory_status = {
                'config_loaded': factory.config is not None,
                'agents_registered': len(factory.get_agent_types()),
                'capabilities_available': len([c.value for c in AgentCapability]),
                'rag_system_available': hasattr(current_app, 'search_system') and getattr(current_app, 'search_system', None) is not None,
                'analytics_available': hasattr(current_app, 'analytics_integration') and getattr(current_app, 'analytics_integration', None) is not None
            }
            
            return jsonify({
                'status': 'success',
                'factory_info': factory_status,
                'system_health': 'operational'
            })
        
        @app.route('/api/enhanced/agents/health', methods=['GET'])
        @agent_error_handler  
        def enhanced_agent_health_check():
            """Health check specifically for enhanced agents."""
            try:
                factory = get_factory()
                
                # Test creating an agent
                test_agent = factory.create_agent('code_analysis')
                
                health_status = {
                    'status': 'healthy',
                    'factory_operational': True,
                    'agent_creation': 'successful',
                    'capabilities_count': len([c.value for c in AgentCapability]),
                    'timestamp': time.time()
                }
                
                return jsonify(health_status)
                
            except Exception as e:
                return jsonify({
                    'status': 'unhealthy', 
                    'factory_operational': False,
                    'error': str(e),
                    'timestamp': time.time()
                }), 500
        
        @app.route('/api/enhanced/agents/benchmark', methods=['POST'])
        @agent_error_handler
        def benchmark_enhanced_agents():
            """Run performance benchmark on enhanced agents."""
            data = request.get_json()
            capability_name = data.get('capability', 'code_analysis')
            test_count = data.get('test_count', 5)
            
            try:
                capability = AgentCapability(capability_name)
            except ValueError:
                return jsonify({'error': f'Unknown capability: {capability_name}'}), 400
            
            # Run benchmark asynchronously
            try:
                from shared_agents.validation.system_validator import AgentValidator
                
                validator = AgentValidator()
                
                # Run benchmark in async context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    metrics = loop.run_until_complete(
                        validator.performance_benchmark(capability, test_count)
                    )
                finally:
                    loop.close()
                
                return jsonify({
                    'status': 'success',
                    'capability': capability_name,
                    'metrics': {
                        'avg_response_time': metrics.avg_response_time,
                        'min_response_time': metrics.min_response_time,
                        'max_response_time': metrics.max_response_time,
                        'success_rate': metrics.success_rate,
                        'throughput': metrics.throughput,
                        'total_executions': metrics.total_executions
                    }
                })
                
            except Exception as e:
                return jsonify({'error': f'Benchmark failed: {str(e)}'}), 500


def register_enhanced_agent_routes(app: Flask):
    """
    Register enhanced agent routes to the Flask app.
    
    Args:
        app: Flask application
    """
    # Create integration
    integration = EnhancedAgentIntegration(app)
    integration.register_routes()
    
    return "Enhanced agent routes registered successfully"
