"""
Flask Routes for Advanced OpenAI Features Integration
"""

import json
import base64
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, request, jsonify, current_app
from werkzeug.utils import secure_filename
import logging

from services.advanced_openai_features import AdvancedOpenAIFeatures

logger = logging.getLogger(__name__)

def register_advanced_openai_routes(app: Flask):
    """Register advanced OpenAI feature routes"""
    
    def get_advanced_features() -> AdvancedOpenAIFeatures:
        """Get or create advanced features instance"""
        if not hasattr(app, 'advanced_openai_features'):
            api_key = app.config.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            
            search_system = getattr(app, 'search_system', None)
            app.advanced_openai_features = AdvancedOpenAIFeatures(api_key, search_system)
        
        return app.advanced_openai_features
    
    # 1. VISION ANALYSIS ROUTES
    @app.route('/api/vision/analyze', methods=['POST'])
    def analyze_image():
        """Analyze image with context using GPT-4o Vision"""
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'No image provided'}), 400
            
            image_file = request.files['image']
            if image_file.filename == '':
                return jsonify({'error': 'No image selected'}), 400
            
            # Get parameters
            analysis_type = request.form.get('analysis_type', 'comprehensive')
            use_context = request.form.get('use_context', 'true').lower() == 'true'
            max_tokens = int(request.form.get('max_tokens', '2000'))
            
            # Read image data
            image_data = image_file.read()
            
            # Get context documents if requested
            context_docs = []
            if use_context and hasattr(app, 'search_system'):
                try:
                    # Search for relevant context
                    search_query = f"image analysis {analysis_type}"
                    search_results = app.search_system.semantic_search(
                        query=search_query,
                        max_results=3
                    )
                    if hasattr(search_results, 'data'):
                        context_docs = [result.content for result in search_results.data]
                except Exception as e:
                    logger.warning(f"Context search failed: {e}")
            
            # Analyze image
            advanced_features = get_advanced_features()
            result = advanced_features.analyze_image_sync(
                image_data=image_data,
                context_documents=context_docs if context_docs else None,
                analysis_type=analysis_type
            )
            
            return jsonify({
                'success': True,
                'analysis': result.analysis,
                'objects_detected': result.objects_detected,
                'text_extracted': result.text_extracted,
                'confidence_scores': result.confidence_scores,
                'context_integration': result.context_integration,
                'usage_stats': result.usage_stats,
                'timestamp': result.timestamp
            })
            
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/vision/capabilities')
    def vision_capabilities():
        """Get vision analysis capabilities"""
        return jsonify({
            'supported_formats': ['png', 'jpg', 'jpeg', 'gif', 'webp'],
            'analysis_types': [
                'comprehensive',
                'technical', 
                'business',
                'creative',
                'accessibility',
                'security',
                'educational'
            ],
            'features': [
                'object_detection',
                'text_extraction',
                'context_integration',
                'detailed_analysis',
                'actionable_insights'
            ],
            'max_image_size': '20MB',
            'max_tokens': 4000
        })
    
    # 2. STRUCTURED OUTPUTS ROUTES
    @app.route('/api/structured/report', methods=['POST'])
    def generate_structured_report():
        """Generate structured reports from data"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            source_data = data.get('data', {})
            report_type = data.get('report_type', 'analysis')
            
            # Define schema based on report type
            schemas = {
                'business': {
                    "type": "object",
                    "properties": {
                        "executive_summary": {"type": "string"},
                        "key_metrics": {
                            "type": "object",
                            "properties": {
                                "revenue": {"type": "number"},
                                "growth_rate": {"type": "number"},
                                "market_share": {"type": "number"}
                            },
                            "required": ["revenue", "growth_rate"]
                        },
                        "recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string"},
                                    "priority": {"type": "string"},
                                    "timeline": {"type": "string"},
                                    "impact": {"type": "string"}
                                },
                                "required": ["action", "priority"]
                            }
                        },
                        "risk_assessment": {"type": "string"}
                    },
                    "required": ["executive_summary", "key_metrics", "recommendations"]
                },
                'technical': {
                    "type": "object",
                    "properties": {
                        "overview": {"type": "string"},
                        "technical_details": {
                            "type": "object",
                            "properties": {
                                "performance_metrics": {"type": "object"},
                                "issues_identified": {"type": "array", "items": {"type": "string"}},
                                "recommendations": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "action_items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "task": {"type": "string"},
                                    "priority": {"type": "string"},
                                    "assignee": {"type": "string"}
                                },
                                "required": ["task", "priority"]
                            }
                        }
                    },
                    "required": ["overview", "technical_details"]
                },
                'analysis': {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "findings": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "insights": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "next_steps": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["summary", "findings"]
                }
            }
            
            schema = schemas.get(report_type, schemas['analysis'])
            
            # Generate structured report
            advanced_features = get_advanced_features()
            structured_report = advanced_features.create_structured_report(
                data=source_data,
                report_schema=schema,
                report_type=report_type
            )
            
            return jsonify({
                'success': True,
                'report': structured_report,
                'report_type': report_type
            })
            
        except Exception as e:
            logger.error(f"Structured report generation failed: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/structured/schemas')
    def get_report_schemas():
        """Get available report schemas"""
        return jsonify({
            'available_schemas': [
                'business',
                'technical', 
                'analysis',
                'financial',
                'research',
                'project_status'
            ],
            'custom_schema_support': True
        })
    
    # 3. REAL-TIME CONVERSATION ROUTES
    @app.route('/api/realtime/session', methods=['POST'])
    def create_realtime_session():
        """Create real-time conversation session"""
        try:
            data = request.get_json() or {}
            session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
            voice = data.get('voice', 'nova')
            instructions = data.get('instructions')
            
            advanced_features = get_advanced_features()
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                session_config = loop.run_until_complete(
                    advanced_features.create_conversation_stream(
                        session_id=session_id,
                        voice=voice,
                        instructions=instructions
                    )
                )
            finally:
                loop.close()
            
            return jsonify({
                'success': True,
                'session': session_config
            })
            
        except Exception as e:
            logger.error(f"Real-time session creation failed: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/realtime/session/<session_id>', methods=['DELETE'])
    def end_realtime_session(session_id: str):
        """End real-time conversation session"""
        try:
            advanced_features = get_advanced_features()
            success = advanced_features.end_conversation_stream(session_id)
            
            return jsonify({
                'success': success,
                'session_id': session_id,
                'status': 'ended' if success else 'not_found'
            })
            
        except Exception as e:
            logger.error(f"Session termination failed: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/realtime/voices')
    def get_realtime_voices():
        """Get available voices for real-time chat"""
        return jsonify({
            'voices': [
                {'id': 'nova', 'name': 'Nova', 'description': 'Bright, energetic voice'},
                {'id': 'alloy', 'name': 'Alloy', 'description': 'Balanced, neutral voice'},
                {'id': 'echo', 'name': 'Echo', 'description': 'Warm, expressive voice'},
                {'id': 'fable', 'name': 'Fable', 'description': 'Clear, articulate voice'},
                {'id': 'onyx', 'name': 'Onyx', 'description': 'Deep, resonant voice'},
                {'id': 'shimmer', 'name': 'Shimmer', 'description': 'Smooth, pleasant voice'}
            ]
        })
    
    # 4. BATCH PROCESSING ROUTES
    @app.route('/api/batch/submit', methods=['POST'])
    def submit_batch_processing():
        """Submit documents for batch processing"""
        try:
            # Handle file uploads
            documents = []
            
            # Process uploaded files
            for key in request.files:
                if key.startswith('file_'):
                    file = request.files[key]
                    if file and file.filename:
                        content = file.read().decode('utf-8', errors='ignore')
                        documents.append({
                            'title': secure_filename(file.filename),
                            'content': content,
                            'source': 'upload'
                        })
            
            # Process JSON data if provided
            if request.is_json:
                data = request.get_json()
                if 'documents' in data:
                    documents.extend(data['documents'])
            
            if not documents:
                return jsonify({'error': 'No documents provided'}), 400
            
            # Get processing parameters
            form_data = request.form.to_dict()
            processing_type = form_data.get('processing_type', 'summarize')
            custom_instructions = form_data.get('custom_instructions')
            
            # Submit batch job
            advanced_features = get_advanced_features()
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                batch_id = loop.run_until_complete(
                    advanced_features.process_documents_batch(
                        documents=documents,
                        processing_type=processing_type,
                        custom_instructions=custom_instructions
                    )
                )
            finally:
                loop.close()
            
            return jsonify({
                'success': True,
                'batch_id': batch_id,
                'document_count': len(documents),
                'processing_type': processing_type
            })
            
        except Exception as e:
            logger.error(f"Batch submission failed: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/batch/status/<batch_id>')
    def get_batch_processing_status(batch_id: str):
        """Get batch processing status"""
        try:
            advanced_features = get_advanced_features()
            status = advanced_features.get_batch_status(batch_id)
            
            return jsonify({
                'success': True,
                'status': status
            })
            
        except Exception as e:
            logger.error(f"Batch status check failed: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/batch/results/<batch_id>')
    def get_batch_processing_results(batch_id: str):
        """Get batch processing results"""
        try:
            advanced_features = get_advanced_features()
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(
                    advanced_features.get_batch_results(batch_id)
                )
            finally:
                loop.close()
            
            return jsonify({
                'success': True,
                'batch_id': batch_id,
                'results': results,
                'total_results': len(results)
            })
            
        except Exception as e:
            logger.error(f"Batch results retrieval failed: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/batch/processing-types')
    def get_batch_processing_types():
        """Get available batch processing types"""
        return jsonify({
            'processing_types': [
                {
                    'id': 'summarize',
                    'name': 'Summarization',
                    'description': 'Generate concise summaries of documents'
                },
                {
                    'id': 'extract_keywords',
                    'name': 'Keyword Extraction',
                    'description': 'Extract main keywords and topics'
                },
                {
                    'id': 'sentiment_analysis',
                    'name': 'Sentiment Analysis',
                    'description': 'Analyze sentiment and tone'
                },
                {
                    'id': 'questions',
                    'name': 'Question Generation',
                    'description': 'Generate relevant questions from content'
                },
                {
                    'id': 'translation',
                    'name': 'Translation',
                    'description': 'Translate documents to different languages'
                },
                {
                    'id': 'custom',
                    'name': 'Custom Processing',
                    'description': 'Use custom instructions for processing'
                }
            ]
        })
    
    # 5. ENHANCED EMBEDDINGS ROUTES
    @app.route('/api/embeddings/enhanced', methods=['POST'])
    def create_enhanced_embeddings():
        """Create enhanced embeddings with metadata"""
        try:
            data = request.get_json()
            if not data or 'texts' not in data:
                return jsonify({'error': 'Texts array required'}), 400
            
            texts = data['texts']
            metadata = data.get('metadata', [])
            dimensions = data.get('dimensions', 3072)
            
            if not isinstance(texts, list):
                return jsonify({'error': 'Texts must be an array'}), 400
            
            advanced_features = get_advanced_features()
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    advanced_features.create_enhanced_embeddings(
                        texts=texts,
                        metadata=metadata if metadata else None,
                        dimensions=dimensions
                    )
                )
            finally:
                loop.close()
            
            return jsonify({
                'success': True,
                'embeddings': result['embeddings'],
                'usage': result['usage'],
                'total_tokens': result['total_tokens'],
                'model': result['model'],
                'dimensions': result['dimensions']
            })
            
        except Exception as e:
            logger.error(f"Enhanced embeddings creation failed: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # 6. FUNCTION CALLING ROUTES
    @app.route('/api/function-calling/agent', methods=['POST'])
    def create_function_calling_agent():
        """Create function calling agent"""
        try:
            data = request.get_json()
            if not data or 'tools' not in data:
                return jsonify({'error': 'Tools array required'}), 400
            
            tools = data['tools']
            instructions = data.get('instructions')
            
            advanced_features = get_advanced_features()
            agent_config = advanced_features.create_function_calling_agent(
                available_tools=tools,
                instructions=instructions
            )
            
            return jsonify({
                'success': True,
                'agent_config': agent_config
            })
            
        except Exception as e:
            logger.error(f"Function calling agent creation failed: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # 7. SYSTEM STATUS ROUTES
    @app.route('/api/advanced/status')
    def get_advanced_features_status():
        """Get status of advanced OpenAI features"""
        try:
            advanced_features = get_advanced_features()
            status = advanced_features.get_system_status()
            
            return jsonify({
                'success': True,
                'status': status
            })
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/advanced/cleanup', methods=['POST'])
    def cleanup_advanced_features():
        """Cleanup expired sessions and batch jobs"""
        try:
            data = request.get_json() or {}
            max_age_hours = data.get('max_age_hours', 24)
            
            advanced_features = get_advanced_features()
            cleanup_result = advanced_features.cleanup_expired_sessions(max_age_hours)
            
            return jsonify({
                'success': True,
                'cleanup_result': cleanup_result
            })
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    logger.info("✅ Advanced OpenAI feature routes registered successfully")
