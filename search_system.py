import logging
import time
from typing import List, Dict, Optional
from openai import OpenAI
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from file_manager import FileUploader
from vector_store_manager import VectorStoreManager
from search_interface import SearchInterface
from vector_store import VectorStore
from config import Config

class SearchSystemError(Exception):
    """Base exception for search system errors"""
    pass

class FileProcessingError(SearchSystemError):
    """Raised when file upload or processing fails"""
    pass

class VectorStoreError(SearchSystemError):
    """Raised when vector store operations fail"""
    pass

class SearchError(SearchSystemError):
    """Raised when search operations fail"""
    pass

class SearchSystem:
    def __init__(self, config: Config | None = None):
        if config:
            self.config = config
            # Validate configuration before using it
            self.config.validate()
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        else:
            # Fallback for backwards compatibility
            self.config = Config()
            self.config.validate()
            self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        
        self.file_uploader = FileUploader(self.client)
        self.vector_store_manager = VectorStoreManager(self.client)
        # Provide a dummy VectorStore for compatibility, but real search uses OpenAI endpoints
        self.search_interface = SearchInterface(vector_store=VectorStore("dummy"), client=self.client)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)
        self.monitoring_enabled = getattr(self.config, 'MONITORING_ENABLED', False)

    def log_performance(self, operation: str, start_time: float, extra: dict = {}):
        duration = time.time() - start_time
        self.logger.info(f"PERF {operation} duration={duration:.3f}s" + (f" {extra}" if extra else ""))
        # Extend here to send metrics to a monitoring system if enabled

    def create_knowledge_base(self, name: str, file_paths: List[str], 
                              metadata: Optional[Dict] = None) -> str:
        start_time = time.time()
        try:
            file_ids = []
            for file_path in file_paths:
                try:
                    file_id = self.file_uploader.upload_file(file_path, metadata)
                    file_ids.append(file_id)
                    self.logger.info(f"Uploaded file {file_path} with ID {file_id}")
                except Exception as e:
                    self.logger.error(f"File upload failed for {file_path}: {str(e)}")
                    raise FileProcessingError(f"File upload failed for {file_path}: {str(e)}") from e
            try:
                vector_store_id = self.vector_store_manager.create_vector_store(name, file_ids)
                self.logger.info(f"Created vector store {name} with ID {vector_store_id}")
            except Exception as e:
                self.logger.error(f"Vector store creation failed: {str(e)}")
                raise VectorStoreError(f"Vector store creation failed: {str(e)}") from e
            try:
                if self.vector_store_manager.wait_for_completion(vector_store_id):
                    self.logger.info("All files processed successfully")
                    vs_id = vector_store_id  # for logging
                    self.log_performance("create_knowledge_base", start_time, {"vector_store_id": vs_id})
                    return vs_id
                else:
                    raise VectorStoreError("File processing did not complete successfully.")
            except Exception as e:
                self.logger.error(f"File processing monitoring failed: {str(e)}")
                raise VectorStoreError(f"File processing monitoring failed: {str(e)}") from e
        except (FileProcessingError, VectorStoreError) as e:
            self.log_performance("create_knowledge_base", start_time, {"error": str(e)})
            raise
        except Exception as e:
            self.log_performance("create_knowledge_base", start_time, {"error": str(e)})
            raise

    def query_knowledge_base(self, vector_store_id: str, query: str, 
                             search_type: str = "assisted") -> Dict:
        start_time = time.time()
        try:
            result = None
            if search_type == "semantic":
                result = self.search_interface.semantic_search(vector_store_id, query)
            elif search_type == "assisted":
                result = self.search_interface.assisted_search([vector_store_id], query)
            else:
                raise ValueError(f"Invalid search type: {search_type}")
            self.log_performance("query_knowledge_base", start_time, {"search_type": search_type})
            return result
        except Exception as e:
            self.log_performance("query_knowledge_base", start_time, {"error": str(e)})
            raise

    def upload_file(self, file_path: str, vector_store_id: str) -> Dict:
        """Upload a file and add it to a vector store."""
        start_time = time.time()
        try:
            # Upload file to OpenAI
            file_id = self.file_uploader.upload_file(file_path)
            
            # Add file to vector store
            self.vector_store_manager.add_files_to_store(vector_store_id, [file_id])
            
            # Get file info
            file_info = self.client.files.retrieve(file_id)
            
            result = {
                'id': file_id,
                'filename': file_info.filename,
                'vector_store_id': vector_store_id
            }
            
            self.log_performance("upload_file", start_time, {"file_id": file_id})
            return result
            
        except Exception as e:
            self.log_performance("upload_file", start_time, {"error": str(e)})
            raise FileProcessingError(f"File upload failed: {str(e)}") from e

    def upload_from_url(self, url: str, vector_store_id: str) -> Dict:
        """Upload a file from URL and add it to a vector store."""
        start_time = time.time()
        try:
            # Upload file from URL
            file_id = self.file_uploader.upload_file(url)
            
            # Add file to vector store
            self.vector_store_manager.add_files_to_store(vector_store_id, [file_id])
            
            # Get file info
            file_info = self.client.files.retrieve(file_id)
            
            result = {
                'id': file_id,
                'filename': file_info.filename,
                'vector_store_id': vector_store_id
            }
            
            self.log_performance("upload_from_url", start_time, {"file_id": file_id})
            return result
            
        except Exception as e:
            self.log_performance("upload_from_url", start_time, {"error": str(e)})
            raise FileProcessingError(f"URL upload failed: {str(e)}") from e

    def list_vector_stores(self) -> List[Dict]:
        """List all vector stores."""
        start_time = time.time()
        try:
            stores = self.client.vector_stores.list()
            result = []
            
            for store in stores.data:
                file_counts = getattr(store, 'file_counts', None)
                if file_counts:
                    file_counts_dict = {
                        'total': getattr(file_counts, 'total', 0),
                        'completed': getattr(file_counts, 'completed', 0),
                        'in_progress': getattr(file_counts, 'in_progress', 0),
                        'failed': getattr(file_counts, 'failed', 0),
                        'cancelled': getattr(file_counts, 'cancelled', 0)
                    }
                else:
                    file_counts_dict = {'total': 0}
                
                store_info = {
                    'id': store.id,
                    'name': store.name,
                    'status': getattr(store, 'status', 'active'),
                    'created_at': getattr(store, 'created_at', None),
                    'file_counts': file_counts_dict
                }
                result.append(store_info)
            
            self.log_performance("list_vector_stores", start_time, {"count": len(result)})
            return result
            
        except Exception as e:
            self.log_performance("list_vector_stores", start_time, {"error": str(e)})
            raise VectorStoreError(f"Failed to list vector stores: {str(e)}") from e

    def create_vector_store(self, name: str) -> Dict:
        """Create a new vector store."""
        start_time = time.time()
        try:
            store = self.client.vector_stores.create(name=name)
            
            file_counts = getattr(store, 'file_counts', None)
            if file_counts:
                file_counts_dict = {
                    'total': getattr(file_counts, 'total', 0),
                    'completed': getattr(file_counts, 'completed', 0),
                    'in_progress': getattr(file_counts, 'in_progress', 0),
                    'failed': getattr(file_counts, 'failed', 0),
                    'cancelled': getattr(file_counts, 'cancelled', 0)
                }
            else:
                file_counts_dict = {'total': 0}
            
            result = {
                'id': store.id,
                'name': store.name,
                'status': getattr(store, 'status', 'active'),
                'created_at': getattr(store, 'created_at', None),
                'file_counts': file_counts_dict
            }
            
            self.log_performance("create_vector_store", start_time, {"store_id": store.id})
            return result
            
        except Exception as e:
            self.log_performance("create_vector_store", start_time, {"error": str(e)})
            raise VectorStoreError(f"Failed to create vector store: {str(e)}") from e

    def delete_vector_store(self, store_id: str) -> None:
        """Delete a vector store."""
        start_time = time.time()
        try:
            self.client.vector_stores.delete(store_id)
            self.log_performance("delete_vector_store", start_time, {"store_id": store_id})
            
        except Exception as e:
            self.log_performance("delete_vector_store", start_time, {"error": str(e)})
            raise VectorStoreError(f"Failed to delete vector store: {str(e)}") from e

    def get_vector_store_status(self, store_id: str) -> Dict:
        """Get the status of a vector store."""
        start_time = time.time()
        try:
            store = self.client.vector_stores.retrieve(store_id)
            
            file_counts = getattr(store, 'file_counts', None)
            if file_counts:
                file_counts_dict = {
                    'total': getattr(file_counts, 'total', 0),
                    'completed': getattr(file_counts, 'completed', 0),
                    'in_progress': getattr(file_counts, 'in_progress', 0),
                    'failed': getattr(file_counts, 'failed', 0),
                    'cancelled': getattr(file_counts, 'cancelled', 0)
                }
            else:
                file_counts_dict = {'total': 0}
            
            result = {
                'id': store.id,
                'name': store.name,
                'status': getattr(store, 'status', 'active'),
                'file_counts': file_counts_dict,
                'created_at': getattr(store, 'created_at', None)
            }
            
            self.log_performance("get_vector_store_status", start_time, {"store_id": store_id})
            return result
            
        except Exception as e:
            self.log_performance("get_vector_store_status", start_time, {"error": str(e)})
            raise VectorStoreError(f"Failed to get vector store status: {str(e)}") from e

    def semantic_search(self, vector_store_id: str, query: str, max_results: int = 10) -> Dict:
        """Perform semantic search on a vector store."""
        start_time = time.time()
        try:
            result = self.search_interface.semantic_search(vector_store_id, query, max_results)
            self.log_performance("semantic_search", start_time, {"vector_store_id": vector_store_id})
            return result
            
        except Exception as e:
            self.log_performance("semantic_search", start_time, {"error": str(e)})
            raise SearchError(f"Semantic search failed: {str(e)}") from e

    def assisted_search(self, vector_store_ids: List[str], query: str) -> Dict:
        """Perform AI-assisted search across multiple vector stores."""
        start_time = time.time()
        try:
            result = self.search_interface.assisted_search(vector_store_ids, query)
            self.log_performance("assisted_search", start_time, {"vector_store_count": len(vector_store_ids)})
            return result
            
        except Exception as e:
            self.log_performance("assisted_search", start_time, {"error": str(e)})
            raise SearchError(f"Assisted search failed: {str(e)}") from e
