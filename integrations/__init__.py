# Integration Module for RAG + Daily Reporting
"""
This module handles the integration between the RAG File Search System
and the Daily Reporting Analytics Platform.
"""

__version__ = "1.0.0"
__author__ = "RAG Integration Team"

from .analytics_integration import AnalyticsIntegration
from .report_ingestion import ReportIngestion

__all__ = ["AnalyticsIntegration", "ReportIngestion"]
