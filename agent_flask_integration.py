"""
Flask Integration for Unified Agent System
Adds 12 specialized agents to the existing RAG + Analytics platform
"""

import os
import json
import time
import asyncio
from typing import Dict, Any, List
from flask import Flask, request, jsonify, render_template
from functools import wraps

from unified_agent_system import (
    UnifiedAgentManager, AgentType, TaskComplexity, 
    create_unified_system, quick_agent_query
)


def register_agent_routes(app: Flask):
    """Register agent-related routes to the existing Flask app."""
    
    # Initialize unified agent system
    unified_agent_system = None
    
    def get_unified_system():
        """Get or create the unified agent system with integrations."""
        nonlocal unified_agent_system
        if unified_agent_system is None:
            # Get RAG and Analytics integrations from app if available
            rag_system = getattr(app, 'search_system', None)
            analytics_integration = getattr(app, 'analytics_integration', None)
            
            unified_agent_system = create_unified_system(
                rag_system=rag_system,
                analytics_integration=analytics_integration
            )
        return unified_agent_system
    
    def agent_error_handler(f):
        """Decorator for consistent agent error handling."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'Agent processing failed',
                    'message': str(e),
                    'agent_system': 'unified_multi_agent'
                }), 500
        return decorated_function
    
    # Main Agent Routes
    
    @app.route('/agents')
    def agents_dashboard():
        """Render the agents dashboard page."""
        return render_template('agents.html')
    
    @app.route('/api/agents/query', methods=['POST'])
    @agent_error_handler
    def agent_query():
        """Process a query through the unified agent system."""
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        context = data.get('context', {})
        agent_type = data.get('agent_type', 'auto')
        
        # Add request metadata to context
        context.update({
            'request_id': f"req_{int(time.time() * 1000)}",
            'timestamp': time.time(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        })
        
        unified_system = get_unified_system()
        
        if agent_type == 'auto':
            # Use intelligent routing
            response = unified_system.process_request(query, context)
        else:
            # Direct agent query
            try:
                result = quick_agent_query(query, agent_type, context)
                response = {
                    'task_id': f"direct_{int(time.time() * 1000)}",
                    'agent_name': agent_type,
                    'result': result,
                    'success': True,
                    'execution_time': 0,
                    'metadata': {'routing': 'direct'}
                }
            except Exception as e:
                return jsonify({'error': f'Direct agent query failed: {str(e)}'}), 400
        
        return jsonify({
            'status': 'success',
            'response': {
                'task_id': response.task_id if hasattr(response, 'task_id') else response.get('task_id'),
                'agent_name': response.agent_name if hasattr(response, 'agent_name') else response.get('agent_name'),
                'result': response.result if hasattr(response, 'result') else response.get('result'),
                'success': response.success if hasattr(response, 'success') else response.get('success'),
                'execution_time': response.execution_time if hasattr(response, 'execution_time') else response.get('execution_time'),
                'metadata': response.metadata if hasattr(response, 'metadata') else response.get('metadata', {})
            }
        })
    
    @app.route('/api/agents/workflow', methods=['POST'])
    @agent_error_handler
    def agent_workflow():
        """Process a complex multi-agent workflow."""
        data = request.get_json()
        if not data or 'task_description' not in data:
            return jsonify({'error': 'Task description is required'}), 400
        
        task_description = data['task_description']
        context = data.get('context', {})
        
        # Add workflow metadata
        context.update({
            'workflow_id': f"workflow_{int(time.time() * 1000)}",
            'timestamp': time.time(),
            'type': 'complex_multi_agent'
        })
        
        unified_system = get_unified_system()
        workflow_responses = unified_system.process_complex_workflow(task_description, context)
        
        return jsonify({
            'status': 'success',
            'workflow': {
                'task_description': task_description,
                'total_steps': len(workflow_responses),
                'execution_summary': {
                    'successful_steps': sum(1 for r in workflow_responses if r.success),
                    'failed_steps': sum(1 for r in workflow_responses if not r.success),
                    'total_execution_time': sum(r.execution_time for r in workflow_responses),
                    'agents_involved': list(set(r.agent_name for r in workflow_responses))
                },
                'responses': [
                    {
                        'task_id': r.task_id,
                        'agent_name': r.agent_name,
                        'result': r.result,
                        'success': r.success,
                        'execution_time': r.execution_time,
                        'metadata': r.metadata,
                        'error': r.error
                    } for r in workflow_responses
                ]
            }
        })
    
    # Individual Agent Endpoints
    
    @app.route('/api/agents/research', methods=['POST'])
    @agent_error_handler
    def research_agent():
        """Direct access to the research agent."""
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Research query is required'}), 400
        
        unified_system = get_unified_system()
        research_agent = unified_system.agents[AgentType.RESEARCH]
        
        result = research_agent.conduct_research(data['query'], data.get('context', {}))
        
        return jsonify({
            'status': 'success',
            'agent': 'Research Analyst',
            'result': result,
            'capabilities': research_agent.specializations
        })
    
    @app.route('/api/agents/performance', methods=['POST'])
    @agent_error_handler
    def performance_agent():
        """Direct access to the performance agent."""
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Performance query is required'}), 400
        
        unified_system = get_unified_system()
        perf_agent = unified_system.agents[AgentType.PERFORMANCE]
        
        result = perf_agent.analyze_performance(data['query'], data.get('context', {}))
        
        return jsonify({
            'status': 'success',
            'agent': 'Performance Analyst',
            'result': result,
            'type': 'performance_analysis'
        })
    
    @app.route('/api/agents/coaching', methods=['POST'])
    @agent_error_handler
    def coaching_agent():
        """Direct access to the coaching agent."""
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Coaching query is required'}), 400
        
        unified_system = get_unified_system()
        coach_agent = unified_system.agents[AgentType.COACHING]
        
        result = coach_agent.provide_coaching(data['query'], data.get('context', {}))
        
        return jsonify({
            'status': 'success',
            'agent': 'AI Coach',
            'result': result,
            'frameworks': coach_agent.coaching_frameworks
        })
    
    @app.route('/api/agents/code/analyze', methods=['POST'])
    @agent_error_handler
    def code_analyzer_agent():
        """Direct access to the code analyzer agent."""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        unified_system = get_unified_system()
        analyzer = unified_system.agents[AgentType.CODE_ANALYZER]
        
        if 'file_path' in data:
            # Analyze specific file
            result = analyzer.analyze()
        else:
            # General code analysis query
            query = data.get('query', 'Analyze code quality and structure')
            result = quick_agent_query(query, 'code_analyzer', data.get('context', {}))
        
        return jsonify({
            'status': 'success',
            'agent': 'Code Analyzer',
            'result': result,
            'analysis_type': 'code_quality'
        })
    
    @app.route('/api/agents/code/debug', methods=['POST'])
    @agent_error_handler
    def code_debugger_agent():
        """Direct access to the code debugger agent."""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        unified_system = get_unified_system()
        debugger = unified_system.agents[AgentType.CODE_DEBUGGER]
        
        if 'file_content' in data:
            # Debug specific code
            file_content = data['file_content']
            diagnostics = debugger.locate_bugs(file_content)
            root_cause = debugger.identify_root_cause(diagnostics)
            
            result = {
                'diagnostics': diagnostics,
                'root_cause': root_cause,
                'execution_trace': debugger.trace_execution(file_content)
            }
        else:
            # General debugging query
            query = data.get('query', 'Help debug code issues')
            result = quick_agent_query(query, 'code_debugger', data.get('context', {}))
        
        return jsonify({
            'status': 'success',
            'agent': 'Code Debugger',
            'result': result,
            'analysis_type': 'debugging'
        })
    
    @app.route('/api/agents/code/repair', methods=['POST'])
    @agent_error_handler
    def code_repair_agent():
        """Direct access to the code repair agent."""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        unified_system = get_unified_system()
        repairer = unified_system.agents[AgentType.CODE_REPAIR]
        
        if 'file_content' in data and 'diagnostics' in data:
            # Repair specific code
            file_content = data['file_content']
            diagnostics = data['diagnostics']
            bug_query = data.get('bug_query')
            
            fixed_content = repairer.generate_fix(file_content, diagnostics, bug_query)
            
            # Test the fix if file path provided
            validation_result = None
            if 'file_path' in data:
                # Write to temp file and test
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                    temp_file.write(fixed_content)
                    temp_path = temp_file.name
                
                validation_result = repairer.test_solution(temp_path)
                os.unlink(temp_path)  # Clean up
            
            result = {
                'original_content': file_content,
                'fixed_content': fixed_content,
                'diagnostics': diagnostics,
                'validation_passed': validation_result
            }
        else:
            # General repair query
            query = data.get('query', 'Help repair code issues')
            result = quick_agent_query(query, 'code_repair', data.get('context', {}))
        
        return jsonify({
            'status': 'success',
            'agent': 'Code Repair',
            'result': result,
            'analysis_type': 'code_repair'
        })
    
    @app.route('/api/agents/test/generate', methods=['POST'])
    @agent_error_handler
    def test_generator_agent():
        """Direct access to the test generator agent."""
        data = request.get_json()
        if not data or 'module_path' not in data:
            return jsonify({'error': 'Module path is required'}), 400
        
        unified_system = get_unified_system()
        test_gen = unified_system.agents[AgentType.TEST_GENERATOR]
        
        module_path = data['module_path']
        bug_trace = data.get('bug_trace')
        
        tests = test_gen.generate_tests(module_path, bug_trace)
        
        return jsonify({
            'status': 'success',
            'agent': 'Test Generator',
            'result': tests,
            'module_path': module_path,
            'test_type': 'automated_pytest'
        })
    
    @app.route('/api/agents/image/analyze', methods=['POST'])
    @agent_error_handler
    def image_agent():
        """Direct access to the image agent."""
        data = request.get_json()
        if not data or 'image_path' not in data:
            return jsonify({'error': 'Image path is required'}), 400
        
        unified_system = get_unified_system()
        img_agent = unified_system.agents[AgentType.IMAGE]
        
        image_path = data['image_path']
        
        # Generate embedding
        embedding = img_agent.embed_image(image_path)
        
        # Generate caption if requested
        caption = None
        if data.get('generate_caption', False):
            prompt = data.get('caption_prompt', 'Describe this image.')
            caption = img_agent.caption(image_path, prompt)
        
        return jsonify({
            'status': 'success',
            'agent': 'Image Analyst',
            'result': {
                'image_path': image_path,
                'embedding_shape': embedding.shape,
                'caption': caption,
                'capabilities': img_agent.capabilities if hasattr(img_agent, 'capabilities') else []
            }
        })
    
    @app.route('/api/agents/audio/transcribe', methods=['POST'])
    @agent_error_handler
    def audio_agent():
        """Direct access to the audio agent."""
        data = request.get_json()
        if not data or 'audio_path' not in data:
            return jsonify({'error': 'Audio path is required'}), 400
        
        unified_system = get_unified_system()
        audio_agent = unified_system.agents[AgentType.AUDIO]
        
        audio_path = data['audio_path']
        
        try:
            transcription = audio_agent.transcribe(audio_path)
            
            return jsonify({
                'status': 'success',
                'agent': 'Audio Processor',
                'result': {
                    'audio_path': audio_path,
                    'transcription': transcription,
                    'capabilities': audio_agent.capabilities if hasattr(audio_agent, 'capabilities') else []
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'agent': 'Audio Processor',
                'error': f'Transcription failed: {str(e)}'
            }), 500
    
    # System Management Routes
    
    @app.route('/api/agents/status')
    @agent_error_handler
    def agent_system_status():
        """Get the status of the unified agent system."""
        unified_system = get_unified_system()
        status = unified_system.get_agent_status()
        
        return jsonify({
            'status': 'success',
            'system': status,
            'timestamp': time.time()
        })
    
    @app.route('/api/agents/optimize', methods=['POST'])
    @agent_error_handler
    def optimize_agent_system():
        """Optimize the agent system performance."""
        unified_system = get_unified_system()
        optimization_report = unified_system.optimize_performance()
        
        return jsonify({
            'status': 'success',
            'optimization': optimization_report,
            'timestamp': time.time()
        })
    
    @app.route('/api/agents/types')
    def agent_types():
        """Get information about all available agent types."""
        agent_info = {
            'core_orchestration': [
                {'type': 'ceo', 'name': 'Chief Executive Officer', 'description': 'Master orchestrator for complex tasks'},
                {'type': 'executor', 'name': 'Executor Agent', 'description': 'Primary task execution with fallback'},
                {'type': 'triage', 'name': 'Triage Specialist', 'description': 'Smart routing and analysis'}
            ],
            'specialized_intelligence': [
                {'type': 'research', 'name': 'Research Analyst', 'description': 'Deep research and information synthesis'},
                {'type': 'performance', 'name': 'Performance Analyst', 'description': 'Business and system performance analysis'},
                {'type': 'coaching', 'name': 'AI Coach', 'description': 'AI-powered coaching and guidance'},
                {'type': 'test_generator', 'name': 'Test Generator', 'description': 'Automated test creation and validation'}
            ],
            'code_intelligence': [
                {'type': 'code_analyzer', 'name': 'Code Analyzer', 'description': 'Advanced code analysis and review'},
                {'type': 'code_debugger', 'name': 'Code Debugger', 'description': 'Intelligent debugging and issue detection'},
                {'type': 'code_repair', 'name': 'Code Repair', 'description': 'Automated code fixing and optimization'}
            ],
            'multimodal_processing': [
                {'type': 'image', 'name': 'Image Analyst', 'description': 'Visual content processing and analysis'},
                {'type': 'audio', 'name': 'Audio Processor', 'description': 'Speech and audio processing'}
            ]
        }
        
        return jsonify({
            'status': 'success',
            'agent_categories': agent_info,
            'total_agents': sum(len(category) for category in agent_info.values())
        })
    
    # Health check for agent system
    @app.route('/api/agents/health')
    def agent_health_check():
        """Health check specifically for the agent system."""
        try:
            unified_system = get_unified_system()
            status = unified_system.get_agent_status()
            
            health_status = {
                'status': 'healthy',
                'agents_available': status['total_agents'],
                'integrations': status['integrations'],
                'memory_usage': status['memory_usage']
            }
            
            # Test basic agent functionality
            try:
                test_response = unified_system.process_request("Health check test query")
                health_status['agent_test'] = 'passed' if test_response.success else 'failed'
            except:
                health_status['agent_test'] = 'failed'
                health_status['status'] = 'degraded'
            
            return jsonify(health_status)
            
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'agent_system': 'failed_to_initialize'
            }), 500

    print("✅ Agent routes registered successfully")
    return app


# Utility function to enhance existing app
def enhance_app_with_agents(app: Flask) -> Flask:
    """Enhance an existing Flask app with agent capabilities."""
    return register_agent_routes(app)


if __name__ == "__main__":
    # Demo standalone agent server
    from flask import Flask
    
    app = Flask(__name__)
    app = register_agent_routes(app)
    
    @app.route('/')
    def index():
        return jsonify({
            'service': 'Unified Agent System API',
            'version': '1.0.0',
            'agents_available': 12,
            'endpoints': [
                '/api/agents/query',
                '/api/agents/workflow', 
                '/api/agents/status',
                '/api/agents/types',
                '/api/agents/health'
            ]
        })
    
    print("🚀 Starting Unified Agent System server...")
    app.run(debug=True, port=5002)
