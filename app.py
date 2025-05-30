"""
Flask web application for the RAG File Search System.
"""
import os
import json
import traceback
from typing import Dict, Any
from flask import Flask, request, jsonify, render_template, current_app
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from search_system import SearchSystem
from config import Config


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    config = Config(config_name)
    
    # Validate configuration before proceeding
    try:
        config.validate()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n🔑 Setup Instructions:")
        print("1. Get your OpenAI API key from: https://platform.openai.com/api-keys")
        print("2. Add it to your .env file: OPENAI_API_KEY=your_actual_api_key")
        print("3. Or run: ./setup_api_key.sh for guided setup")
        print("\n📖 See README.md for more details\n")
        raise
    
    app.config.update(config.to_dict())
    
    # Enable CORS
    CORS(app)
    
    # Initialize search system
    search_system = SearchSystem(config)
    app.search_system = search_system
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register routes
    register_routes(app)
    
    return app


def register_error_handlers(app: Flask):
    """Register error handlers for the application."""
    
    @app.errorhandler(413)
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(error):
        return jsonify({
            'error': 'File too large',
            'message': 'The uploaded file exceeds the maximum size limit.',
            'max_size': app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        }), 413
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found.'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500


def register_routes(app: Flask):
    """Register application routes."""
    
    @app.route('/')
    def index():
        """Render the main application page."""
        return render_template('index.html')
    
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        try:
            # Test OpenAI API connection
            current_app.search_system.client.models.list()
            api_status = 'connected'
        except Exception as e:
            api_status = f'error: {str(e)}'
        
        return jsonify({
            'status': 'healthy' if api_status == 'connected' else 'degraded',
            'service': 'RAG File Search System',
            'version': '1.0.0',
            'openai_api': api_status
        })
    
    @app.route('/api/test-api-key')
    def test_api_key():
        """Test if the OpenAI API key is working."""
        try:
            # Simple test to verify API key works
            models = current_app.search_system.client.models.list()
            return jsonify({
                'status': 'success',
                'message': 'OpenAI API key is working correctly',
                'available_models': len(models.data)
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'OpenAI API key test failed: {str(e)}',
                'suggestion': 'Please check your OPENAI_API_KEY in the .env file'
            }), 401
    
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """Upload a file to the system."""
        try:
            if 'file' not in request.files and 'url' not in request.form:
                return jsonify({
                    'error': 'No file or URL provided',
                    'message': 'Please provide either a file or URL to upload.'
                }), 400
            
            vector_store_id = request.form.get('vector_store_id')
            if not vector_store_id:
                return jsonify({
                    'error': 'Vector store ID required',
                    'message': 'Please provide a vector store ID.'
                }), 400
            
            # Handle file upload
            if 'file' in request.files:
                file = request.files['file']
                if file.filename == '':
                    return jsonify({
                        'error': 'No file selected',
                        'message': 'Please select a file to upload.'
                    }), 400
                
                # Save file temporarily
                filename = secure_filename(file.filename)
                temp_path = os.path.join('/tmp', filename)
                file.save(temp_path)
                
                # Upload to vector store
                result = app.search_system.upload_file(temp_path, vector_store_id)
                
                # Clean up temporary file
                os.unlink(temp_path)
                
            # Handle URL upload
            elif 'url' in request.form:
                url = request.form['url']
                result = app.search_system.upload_from_url(url, vector_store_id)
            
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'file_id': result.get('id'),
                'filename': result.get('filename')
            })
            
        except Exception as e:
            current_app.logger.error(f"Upload error: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'error': 'Upload failed',
                'message': str(e)
            }), 500
    
    @app.route('/api/vector-stores', methods=['GET'])
    def list_vector_stores():
        """List all vector stores."""
        try:
            stores = app.search_system.list_vector_stores()
            return jsonify({
                'success': True,
                'vector_stores': stores
            })
        except Exception as e:
            current_app.logger.error(f"List vector stores error: {str(e)}")
            return jsonify({
                'error': 'Failed to list vector stores',
                'message': str(e)
            }), 500
    
    @app.route('/api/vector-stores', methods=['POST'])
    def create_vector_store():
        """Create a new vector store."""
        try:
            data = request.get_json()
            name = data.get('name')
            if not name:
                return jsonify({
                    'error': 'Name required',
                    'message': 'Vector store name is required.'
                }), 400
            
            store = app.search_system.create_vector_store(name)
            return jsonify({
                'success': True,
                'message': 'Vector store created successfully',
                'vector_store': store
            })
            
        except Exception as e:
            current_app.logger.error(f"Create vector store error: {str(e)}")
            return jsonify({
                'error': 'Failed to create vector store',
                'message': str(e)
            }), 500
    
    @app.route('/api/vector-stores/<store_id>', methods=['DELETE'])
    def delete_vector_store(store_id):
        """Delete a vector store."""
        try:
            app.search_system.delete_vector_store(store_id)
            return jsonify({
                'success': True,
                'message': 'Vector store deleted successfully'
            })
            
        except Exception as e:
            current_app.logger.error(f"Delete vector store error: {str(e)}")
            return jsonify({
                'error': 'Failed to delete vector store',
                'message': str(e)
            }), 500
    
    @app.route('/api/search', methods=['POST'])
    def search():
        """Perform a search query."""
        try:
            data = request.get_json()
            query = data.get('query')
            vector_store_ids = data.get('vector_store_ids', [])
            search_type = data.get('search_type', 'assisted')
            max_results = data.get('max_results', 10)
            
            if not query:
                return jsonify({
                    'error': 'Query required',
                    'message': 'Search query is required.'
                }), 400
            
            if not vector_store_ids:
                return jsonify({
                    'error': 'Vector store IDs required',
                    'message': 'At least one vector store ID is required.'
                }), 400
            
            # Perform search based on type
            if search_type == 'semantic':
                results = app.search_system.semantic_search(
                    vector_store_ids[0], query, max_results
                )
            elif search_type == 'assisted':
                results = app.search_system.assisted_search(
                    vector_store_ids, query
                )
            else:
                return jsonify({
                    'error': 'Invalid search type',
                    'message': 'Search type must be "semantic" or "assisted".'
                }), 400
            
            return jsonify({
                'success': True,
                'query': query,
                'search_type': search_type,
                'results': results
            })
            
        except Exception as e:
            current_app.logger.error(f"Search error: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'error': 'Search failed',
                'message': str(e)
            }), 500
    
    @app.route('/api/vector-stores/<store_id>/status')
    def vector_store_status(store_id):
        """Get vector store status."""
        try:
            status = app.search_system.get_vector_store_status(store_id)
            return jsonify({
                'success': True,
                'status': status
            })
        except Exception as e:
            current_app.logger.error(f"Status check error: {str(e)}")
            return jsonify({
                'error': 'Failed to get status',
                'message': str(e)
            }), 500


if __name__ == '__main__':
    import sys
    
    # Allow port to be specified as command line argument
    port = 5001  # Default to 5001 to avoid AirPlay Receiver conflict
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 5001.")
    
    # Allow port from environment variable
    port = int(os.getenv('FLASK_RUN_PORT', port))
    
    app = create_app()
    print(f"\n🚀 RAG File Search System starting on port {port}")
    print(f"📱 Open your browser to: http://localhost:{port}")
    print("🔑 Make sure your OpenAI API key is configured in .env file\n")
    
    app.run(debug=True, host='0.0.0.0', port=port)
