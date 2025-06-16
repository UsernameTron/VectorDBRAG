"""
Subpackage for enhanced agent implementations.
"""

# Import all enhanced agents
from .enhanced_agents import (
    CEOAgent,
    ResearchAgent,
    CodeAnalysisAgent,
    TriageAgent,
    CodeDebuggerAgent,
    CodeRepairAgent,
    PerformanceProfilerAgent,
    TestGeneratorAgent,
    ImageAgent,
    AudioAgent
)

# Import brand-specific agents
from .brand_agents import (
    BrandDeconstructionAgent,
    GPTImageGenerationAgent,
    BrandIntelligenceAgent,
    BrandAnalysisRequest,
    BrandAnalysisResult
)

# Import factory
from .factory import EnhancedAgentFactory

__all__ = [
    # Core enhanced agents
    'CEOAgent',
    'ResearchAgent', 
    'CodeAnalysisAgent',
    'TriageAgent',
    'CodeDebuggerAgent',
    'CodeRepairAgent',
    'PerformanceProfilerAgent',
    'TestGeneratorAgent',
    'ImageAgent',
    'AudioAgent',
    
    # Brand agents
    'BrandDeconstructionAgent',
    'GPTImageGenerationAgent',
    'BrandIntelligenceAgent',
    
    # Request/Response classes
    'BrandAnalysisRequest',
    'BrandAnalysisResult',
    
    # Factory
    'EnhancedAgentFactory'
]