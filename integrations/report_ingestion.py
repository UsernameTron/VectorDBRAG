"""
Report Ingestion Module

Handles automatic ingestion of analytics reports into the RAG knowledge base.
"""

import os
import json
import logging
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from search_system import SearchSystem
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportIngestionHandler(FileSystemEventHandler):
    """File system event handler for automatic report ingestion."""
    
    def __init__(self, rag_system: SearchSystem, target_vector_store: str, get_vector_store_id_func):
        self.rag_system = rag_system
        self.target_vector_store = target_vector_store
        self.get_vector_store_id = get_vector_store_id_func
        self.supported_extensions = {'.pdf', '.txt', '.docx', '.md', '.json', '.csv'}
        
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            self._process_new_file(event.src_path)
            
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            self._process_new_file(event.src_path)
            
    def _process_new_file(self, file_path: str):
        """Process a new or modified file."""
        file_path = Path(file_path)
        
        # Check if it's a supported file type
        if file_path.suffix.lower() in self.supported_extensions:
            # Add a small delay to ensure file write is complete
            time.sleep(2)
            
            try:
                logger.info(f"Auto-ingesting new report: {file_path}")
                # Get vector store ID
                vector_store_id = self.get_vector_store_id(self.target_vector_store)
                result = self.rag_system.upload_file(
                    file_path=str(file_path),
                    vector_store_id=vector_store_id
                )
                logger.info(f"Successfully ingested: {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")


class ReportIngestion:
    """
    Manages automatic ingestion of reports from the Daily Reporting system
    into the RAG knowledge base.
    """
    
    def __init__(self, rag_system: SearchSystem, analytics_path: str = "Daily_Reporting"):
        """
        Initialize the report ingestion system.
        
        Args:
            rag_system: The RAG search system instance
            analytics_path: Path to the Daily Reporting system
        """
        self.rag_system = rag_system
        self.analytics_path = Path(analytics_path)
        self.reports_kb_name = "Business_Analytics_Reports"
        self.reports_directory = self.analytics_path / "reports"
        self.observer = None
        
        # Ensure reports directory exists
        self.reports_directory.mkdir(exist_ok=True)
        
        # Setup ingestion tracking
        self.ingestion_log = []
        
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
        
    def start_auto_ingestion(self):
        """Start automatic file monitoring and ingestion."""
        try:
            # Create event handler
            event_handler = ReportIngestionHandler(
                self.rag_system, 
                self.reports_kb_name,
                self._get_or_create_vector_store
            )
            
            # Setup file system observer
            self.observer = Observer()
            self.observer.schedule(
                event_handler, 
                str(self.reports_directory), 
                recursive=True
            )
            
            # Start monitoring
            self.observer.start()
            logger.info(f"Started auto-ingestion monitoring: {self.reports_directory}")
            
            # Schedule periodic bulk ingestion
            schedule.every(1).hours.do(self._periodic_ingestion)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start auto-ingestion: {e}")
            return False
            
    def stop_auto_ingestion(self):
        """Stop automatic file monitoring."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            logger.info("Stopped auto-ingestion monitoring")
            
    def manual_bulk_ingestion(self) -> Dict[str, Any]:
        """
        Manually ingest all reports in the reports directory.
        
        Returns:
            Dictionary with ingestion results
        """
        results = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'details': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Find all report files
            report_files = []
            for ext in ['.pdf', '.txt', '.docx', '.md', '.json', '.csv']:
                report_files.extend(self.reports_directory.glob(f'**/*{ext}'))
                
            results['total_files'] = len(report_files)
            
            # Get vector store ID once
            vector_store_id = self._get_or_create_vector_store(self.reports_kb_name)
            
            # Process each file
            for file_path in report_files:
                try:
                    # Check if file was recently ingested
                    if not self._should_ingest_file(file_path):
                        continue
                        
                    # Attempt ingestion
                    upload_result = self.rag_system.upload_file(
                        file_path=str(file_path),
                        vector_store_id=vector_store_id
                    )
                    
                    results['successful'] += 1
                    results['details'].append({
                        'file': str(file_path),
                        'status': 'success',
                        'result': upload_result
                    })
                    
                    # Log successful ingestion
                    self._log_ingestion(file_path, 'success')
                    
                except Exception as e:
                    results['failed'] += 1
                    results['details'].append({
                        'file': str(file_path),
                        'status': 'failed',
                        'error': str(e)
                    })
                    
                    # Log failed ingestion
                    self._log_ingestion(file_path, 'failed', str(e))
                    
            logger.info(f"Bulk ingestion complete: {results['successful']} successful, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Bulk ingestion failed: {e}")
            results['error'] = str(e)
            return results
            
    def _periodic_ingestion(self):
        """Periodic bulk ingestion scheduled task."""
        logger.info("Running periodic bulk ingestion...")
        results = self.manual_bulk_ingestion()
        logger.info(f"Periodic ingestion completed: {results['successful']} files processed")
        
    def _should_ingest_file(self, file_path: Path) -> bool:
        """
        Check if a file should be ingested (not recently processed).
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be ingested
        """
        # Check modification time
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        if mod_time < datetime.now() - timedelta(days=7):
            return False  # Don't re-ingest old files
            
        # Check ingestion log
        file_str = str(file_path)
        for log_entry in self.ingestion_log:
            if (log_entry['file'] == file_str and 
                log_entry['status'] == 'success' and
                datetime.fromisoformat(log_entry['timestamp']) > mod_time):
                return False  # Already successfully ingested
                
        return True
        
    def _log_ingestion(self, file_path: Path, status: str, error: Optional[str] = None):
        """Log an ingestion attempt."""
        log_entry = {
            'file': str(file_path),
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'file_size': file_path.stat().st_size if file_path.exists() else 0
        }
        
        if error:
            log_entry['error'] = error
            
        self.ingestion_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.ingestion_log) > 1000:
            self.ingestion_log = self.ingestion_log[-1000:]
            
    def get_ingestion_status(self) -> Dict[str, Any]:
        """Get current ingestion status and statistics."""
        # Calculate statistics
        recent_logs = [
            log for log in self.ingestion_log 
            if datetime.fromisoformat(log['timestamp']) > datetime.now() - timedelta(days=7)
        ]
        
        successful = len([log for log in recent_logs if log['status'] == 'success'])
        failed = len([log for log in recent_logs if log['status'] == 'failed'])
        
        return {
            'monitoring_active': self.observer is not None and self.observer.is_alive(),
            'reports_directory': str(self.reports_directory),
            'target_vector_store': self.reports_kb_name,
            'recent_ingestions': {
                'successful': successful,
                'failed': failed,
                'total': len(recent_logs)
            },
            'last_ingestion': self.ingestion_log[-1] if self.ingestion_log else None,
            'status_check_time': datetime.now().isoformat()
        }
        
    def create_sample_reports(self):
        """Create sample reports for testing."""
        sample_reports = [
            {
                'filename': 'daily_performance_report.md',
                'content': '''# Daily Performance Report - {date}

## Executive Summary
- Total calls handled: 1,250
- Average response time: 2.3 minutes
- Customer satisfaction: 94%
- Agent utilization: 87%

## Key Metrics
- Escalation rate: 5.2%
- First call resolution: 89%
- Agent performance variance: 12%

## Recommendations
1. Focus coaching on agents with high escalation rates
2. Review knowledge base for common escalation topics
3. Consider additional training on product features
'''.format(date=datetime.now().strftime('%Y-%m-%d'))
            },
            {
                'filename': 'weekly_analytics_summary.md',
                'content': '''# Weekly Analytics Summary - Week of {date}

## Performance Trends
- Week-over-week improvement in response times
- Customer satisfaction stable at 94%
- New agent onboarding successful

## Areas of Focus
1. Peak hour staffing optimization
2. Knowledge base updates needed
3. Customer feedback integration

## Action Items
- Schedule team coaching session
- Update FAQ documentation
- Review escalation procedures
'''.format(date=datetime.now().strftime('%Y-%m-%d'))
            }
        ]
        
        for report in sample_reports:
            file_path = self.reports_directory / report['filename']
            with open(file_path, 'w') as f:
                f.write(report['content'])
                
        logger.info(f"Created {len(sample_reports)} sample reports")
        return len(sample_reports)
        
    def run_ingestion_service(self):
        """Run the ingestion service (blocking call for daemon mode)."""
        try:
            # Start auto-ingestion
            if not self.start_auto_ingestion():
                logger.error("Failed to start auto-ingestion")
                return
                
            logger.info("Report ingestion service started. Press Ctrl+C to stop.")
            
            # Keep the service running
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Shutting down ingestion service...")
            self.stop_auto_ingestion()
        except Exception as e:
            logger.error(f"Ingestion service error: {e}")
            self.stop_auto_ingestion()


# Example usage and testing
def test_ingestion():
    """Test the report ingestion functionality."""
    try:
        # Initialize ingestion system
        config = Config()
        rag_system = SearchSystem(config)
        ingestion = ReportIngestion(rag_system)
        
        # Create sample reports
        ingestion.create_sample_reports()
        
        # Test manual bulk ingestion
        results = ingestion.manual_bulk_ingestion()
        print("Ingestion Results:", json.dumps(results, indent=2))
        
        # Get status
        status = ingestion.get_ingestion_status()
        print("Ingestion Status:", json.dumps(status, indent=2))
        
    except Exception as e:
        logger.error(f"Ingestion test failed: {e}")


if __name__ == "__main__":
    # Run ingestion test
    test_ingestion()
