"""
Analytics Integration Module

This module provides integration between the RAG File Search System
and the Daily Reporting Analytics Platform.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from search_system import SearchSystem
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsIntegration:
    """
    Handles integration between RAG system and Daily Reporting analytics.
    
    Features:
    - Unified web interface
    - Cross-system data queries
    - Report auto-ingestion
    - Context-aware analytics
    """
    
    def __init__(self, rag_system: SearchSystem, analytics_path: str = "Daily_Reporting"):
        """
        Initialize the analytics integration.
        
        Args:
            rag_system: The RAG search system instance
            analytics_path: Path to the Daily Reporting system
        """
        self.rag_system = rag_system
        self.analytics_path = Path(analytics_path)
        self.reports_kb_name = "Business_Analytics_Reports"
        
        # Setup analytics integration
        self._setup_integration()
        
    def _setup_integration(self):
        """Setup the integration environment."""
        try:
            # Create business reports knowledge base if it doesn't exist
            existing_stores = self.rag_system.list_vector_stores()
            store_names = [store.get('name', '') for store in existing_stores]
            
            if self.reports_kb_name not in store_names:
                logger.info(f"Creating {self.reports_kb_name} knowledge base...")
                self.rag_system.create_vector_store(self.reports_kb_name)
                
            logger.info("Analytics integration setup complete")
            
        except Exception as e:
            logger.error(f"Error setting up analytics integration: {e}")
            
    def _get_or_create_vector_store(self, name: str) -> str:
        """
        Get vector store ID by name, or create if it doesn't exist.
        
        Args:
            name: Name of the vector store
            
        Returns:
            Vector store ID
        """
        try:
            # List all vector stores to find by name
            vector_stores = self.rag_system.list_vector_stores()
            
            # Look for existing store with this name
            for store in vector_stores:
                if store.get('name') == name:
                    return store['id']
            
            # Create new vector store if not found
            logger.info(f"Creating new vector store: {name}")
            vector_store_id = self.rag_system.vector_store_manager.create_vector_store(name)
            logger.info(f"Created vector store '{name}' with ID: {vector_store_id}")
            return vector_store_id
            
        except Exception as e:
            logger.error(f"Error getting/creating vector store '{name}': {e}")
            raise
            
    async def get_analytics_dashboard_data(self) -> Dict[str, Any]:
        """
        Get dashboard data combining RAG and analytics systems.
        
        Returns:
            Dictionary containing dashboard data
        """
        try:
            # Get RAG system status
            rag_status = {
                'vector_stores': len(self.rag_system.list_vector_stores()),
                'health': 'healthy'
            }
            
            # Get analytics data (placeholder - will integrate with actual analytics)
            analytics_status = {
                'reports_generated_today': 5,
                'active_agents': 25,
                'health': 'healthy'
            }
            
            # Get recent searches from business reports
            recent_searches = await self._get_recent_business_queries()
            
            return {
                'rag_status': rag_status,
                'analytics_status': analytics_status,
                'recent_searches': recent_searches,
                'integration_status': 'active',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {
                'error': str(e),
                'integration_status': 'error',
                'last_updated': datetime.now().isoformat()
            }
            
    async def _get_recent_business_queries(self) -> List[Dict[str, Any]]:
        """Get recent queries related to business analytics."""
        # Placeholder for recent query tracking
        # In a full implementation, this would track actual user queries
        return [
            {
                'query': 'Q3 performance metrics',
                'timestamp': datetime.now().isoformat(),
                'results_count': 12
            },
            {
                'query': 'customer satisfaction trends',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'results_count': 8
            }
        ]
        
    async def search_business_intelligence(self, query: str, search_type: str = "assisted") -> Dict[str, Any]:
        """
        Enhanced search that combines RAG document search with analytics context.
        
        Args:
            query: The search query
            search_type: Type of search ("semantic" or "assisted")
            
        Returns:
            Enhanced search results with analytics context
        """
        try:
            # Get vector store ID for analytics reports
            vector_store_id = self._get_or_create_vector_store(self.reports_kb_name)
            
            # Perform standard RAG search and convert to serializable format
            try:
                if search_type == "semantic":
                    search_response = self.rag_system.semantic_search(
                        vector_store_id=vector_store_id,
                        query=query
                    )
                    # Convert to a safe dictionary format
                    results = {
                        'type': 'semantic',
                        'results': str(search_response),  # Safe fallback
                        'query': query
                    }
                else:
                    # For assisted search
                    response = self.rag_system.assisted_search(
                        vector_store_ids=[vector_store_id],
                        query=query
                    )
                    # Convert to safe format
                    results = {
                        'type': 'assisted',
                        'response': str(response),  # Safe fallback
                        'query': query
                    }
                    
            except Exception as search_error:
                logger.error(f"Search error: {search_error}")
                results = {
                    'type': search_type,
                    'error': str(search_error),
                    'query': query
                }
            
            # Add analytics context (placeholder for actual analytics integration)
            analytics_context = await self._get_analytics_context(query)
            
            return {
                'search_results': results,
                'analytics_context': analytics_context,
                'search_type': search_type,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in business intelligence search: {e}")
            return {
                'error': str(e),
                'search_type': search_type,
                'timestamp': datetime.now().isoformat()
            }
            
    async def _get_analytics_context(self, query: str) -> Dict[str, Any]:
        """Get relevant analytics context for a query."""
        # Placeholder for analytics context
        # This would integrate with the actual Daily Reporting system
        return {
            'related_metrics': ['customer_satisfaction', 'response_time'],
            'time_period': 'last_30_days',
            'trending_topics': ['performance improvement', 'agent coaching']
        }
        
    def get_integration_health(self) -> Dict[str, Any]:
        """Check the health of the integration."""
        health_status = {
            'rag_system': 'healthy',
            'analytics_path_exists': self.analytics_path.exists(),
            'reports_kb_exists': self.reports_kb_name in [
                store.get('name', '') for store in self.rag_system.list_vector_stores()
            ],
            'integration_active': True,
            'last_check': datetime.now().isoformat()
        }
        
        return health_status
        
    def ingest_analytics_report(self, report_path: str, report_metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Ingest an analytics report into the RAG knowledge base.
        
        Args:
            report_path: Path to the report file
            report_metadata: Optional metadata about the report
            
        Returns:
            Ingestion result
        """
        try:
            # Get vector store ID
            vector_store_id = self._get_or_create_vector_store(self.reports_kb_name)
            
            # Upload the report file to the business reports knowledge base
            result = self.rag_system.upload_file(
                file_path=report_path,
                vector_store_id=vector_store_id
            )
            
            logger.info(f"Successfully ingested report: {report_path}")
            return {
                'success': True,
                'file_path': report_path,
                'vector_store': self.reports_kb_name,
                'metadata': report_metadata,
                'ingestion_time': datetime.now().isoformat(),
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Error ingesting report {report_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': report_path,
                'ingestion_time': datetime.now().isoformat()
            }


# Example usage and testing functions
async def test_integration():
    """Test the analytics integration functionality."""
    try:
        # Initialize the integration
        config = Config()
        rag_system = SearchSystem(config)
        integration = AnalyticsIntegration(rag_system)
        
        # Test dashboard data
        dashboard_data = await integration.get_analytics_dashboard_data()
        print("Dashboard Data:", json.dumps(dashboard_data, indent=2))
        
        # Test business intelligence search
        search_results = await integration.search_business_intelligence(
            "quarterly performance metrics"
        )
        print("Search Results:", json.dumps(search_results, indent=2))
        
        # Test health check
        health = integration.get_integration_health()
        print("Integration Health:", json.dumps(health, indent=2))
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}")


if __name__ == "__main__":
    # Run integration test
    asyncio.run(test_integration())
