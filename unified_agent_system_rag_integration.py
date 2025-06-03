"""
Unified Agent System RAG Integration
Connects the 12 specialized agents with RAG Search capabilities for enhanced code improvement
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Import from existing systems
from unified_agent_system import (
    UnifiedAgentManager, AgentType, TaskComplexity, AgentTask, AgentResponse,
    create_unified_system
)
from search_system import SearchSystem


class RAGQueryType(Enum):
    """Types of RAG queries for different code improvement tasks."""
    CODE_ANALYSIS = "code_analysis"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    DEBUGGING_PATTERNS = "debugging_patterns"
    BEST_PRACTICES = "best_practices"
    SECURITY_REVIEW = "security_review"
    TESTING_STRATEGIES = "testing_strategies"


@dataclass
class RAGEnhancedQuery:
    """Enhanced query with RAG context for agent processing."""
    original_query: str
    rag_context: Dict[str, Any]
    query_type: RAGQueryType
    vector_store_ids: List[str]
    confidence_score: float = 0.0
    sources: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []


class RAGEnhancedAgent:
    """Enhanced agent with RAG search capabilities for code improvement."""
    
    def __init__(self, base_agent, rag_system: SearchSystem, agent_type: AgentType):
        """
        Initialize RAG-enhanced agent.
        
        Args:
            base_agent: The original agent instance
            rag_system: RAG search system for knowledge lookup
            agent_type: Type of agent for specialized RAG queries
        """
        self.base_agent = base_agent
        self.rag_system = rag_system
        self.agent_type = agent_type
        self.name = getattr(base_agent, 'name', f"RAG-Enhanced {agent_type.value}")
        
        # Define RAG specializations for different agent types
        self.rag_specializations = {
            AgentType.CODE_ANALYZER: [RAGQueryType.CODE_ANALYSIS, RAGQueryType.BEST_PRACTICES],
            AgentType.CODE_DEBUGGER: [RAGQueryType.DEBUGGING_PATTERNS, RAGQueryType.TESTING_STRATEGIES],
            AgentType.CODE_REPAIR: [RAGQueryType.DEBUGGING_PATTERNS, RAGQueryType.BEST_PRACTICES],
            AgentType.PERFORMANCE: [RAGQueryType.PERFORMANCE_OPTIMIZATION, RAGQueryType.BEST_PRACTICES],
            AgentType.TEST_GENERATOR: [RAGQueryType.TESTING_STRATEGIES, RAGQueryType.BEST_PRACTICES],
            AgentType.CEO: [RAGQueryType.BEST_PRACTICES, RAGQueryType.SECURITY_REVIEW],
            AgentType.RESEARCH: [RAGQueryType.BEST_PRACTICES, RAGQueryType.CODE_ANALYSIS]
        }
    
    async def enhanced_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> RAGEnhancedQuery:
        """
        Enhance a query with RAG search results.
        
        Args:
            query: Original query
            context: Additional context for the query
            
        Returns:
            Enhanced query with RAG context
        """
        context = context or {}
        
        # Determine appropriate RAG query types for this agent
        query_types = self.rag_specializations.get(self.agent_type, [RAGQueryType.BEST_PRACTICES])
        
        # Perform RAG searches for relevant knowledge
        rag_context = {}
        all_sources = []
        
        for query_type in query_types:
            try:
                # Create specialized search query based on type and original query
                search_query = self._create_specialized_query(query, query_type)
                
                # Search relevant vector stores (assumes code/tech knowledge bases exist)
                vector_store_ids = self._get_relevant_vector_stores(query_type)
                
                if vector_store_ids:
                    # Perform assisted search for comprehensive results
                    search_results = self.rag_system.assisted_search(vector_store_ids, search_query)
                    
                    rag_context[query_type.value] = search_results
                    
                    # Extract sources for citation
                    if isinstance(search_results, dict) and 'sources' in search_results:
                        all_sources.extend(search_results.get('sources', []))
                        
            except Exception as e:
                print(f"⚠️ RAG search failed for {query_type.value}: {e}")
                rag_context[query_type.value] = {"error": str(e)}
        
        return RAGEnhancedQuery(
            original_query=query,
            rag_context=rag_context,
            query_type=query_types[0] if query_types else RAGQueryType.BEST_PRACTICES,
            vector_store_ids=self._get_relevant_vector_stores(query_types[0] if query_types else RAGQueryType.BEST_PRACTICES),
            confidence_score=self._calculate_confidence_score(rag_context),
            sources=all_sources
        )
    
    def _create_specialized_query(self, original_query: str, query_type: RAGQueryType) -> str:
        """Create specialized search query based on query type."""
        query_templates = {
            RAGQueryType.CODE_ANALYSIS: f"Code analysis patterns and best practices for: {original_query}",
            RAGQueryType.PERFORMANCE_OPTIMIZATION: f"Performance optimization techniques for: {original_query}",
            RAGQueryType.DEBUGGING_PATTERNS: f"Common debugging patterns and solutions for: {original_query}",
            RAGQueryType.BEST_PRACTICES: f"Best practices and coding standards for: {original_query}",
            RAGQueryType.SECURITY_REVIEW: f"Security considerations and patterns for: {original_query}",
            RAGQueryType.TESTING_STRATEGIES: f"Testing strategies and patterns for: {original_query}"
        }
        
        return query_templates.get(query_type, original_query)
    
    def _get_relevant_vector_stores(self, query_type: RAGQueryType) -> List[str]:
        """Get relevant vector store IDs based on query type."""
        # This would be configured based on your knowledge base organization
        # For now, return empty list - would be populated with actual vector store IDs
        # Example: {"code_knowledge", "best_practices_kb", "performance_kb", etc.}
        return []
    
    def _calculate_confidence_score(self, rag_context: Dict[str, Any]) -> float:
        """Calculate confidence score based on RAG results quality."""
        if not rag_context:
            return 0.0
        
        successful_queries = sum(1 for result in rag_context.values() 
                               if isinstance(result, dict) and 'error' not in result)
        total_queries = len(rag_context)
        
        return successful_queries / total_queries if total_queries > 0 else 0.0
    
    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Run the enhanced agent with RAG context.
        
        Args:
            query: The query to process
            context: Additional context
            
        Returns:
            Enhanced response with RAG knowledge
        """
        try:
            # Get RAG-enhanced query
            enhanced_query = asyncio.run(self.enhanced_query(query, context))
            
            # Create enhanced context for the base agent
            enhanced_context = context or {}
            enhanced_context.update({
                'rag_context': enhanced_query.rag_context,
                'confidence_score': enhanced_query.confidence_score,
                'sources': enhanced_query.sources,
                'query_type': enhanced_query.query_type.value
            })
            
            # Prepare enhanced prompt with RAG context
            enhanced_prompt = self._create_enhanced_prompt(query, enhanced_query)
            
            # Run base agent with enhanced prompt
            if hasattr(self.base_agent, 'run'):
                base_response = self.base_agent.run(enhanced_prompt)
            else:
                base_response = f"Agent {self.name} processed: {enhanced_prompt}"
            
            # Format response with RAG citations
            final_response = self._format_response_with_citations(base_response, enhanced_query)
            
            return final_response
            
        except Exception as e:
            print(f"⚠️ RAG-enhanced agent error: {e}")
            # Fallback to base agent
            if hasattr(self.base_agent, 'run'):
                return self.base_agent.run(query)
            else:
                return f"Agent {self.name} processed: {query}"
    
    def _create_enhanced_prompt(self, original_query: str, enhanced_query: RAGEnhancedQuery) -> str:
        """Create enhanced prompt with RAG context."""
        context_summary = ""
        
        if enhanced_query.rag_context:
            context_summary = "\n\n**Relevant Knowledge Context:**\n"
            for query_type, results in enhanced_query.rag_context.items():
                if isinstance(results, dict) and 'error' not in results:
                    context_summary += f"- {query_type.replace('_', ' ').title()}: Available\n"
        
        enhanced_prompt = f"""
{original_query}

{context_summary}

Please provide a comprehensive response that incorporates the relevant knowledge context above.
Focus on best practices, proven patterns, and actionable recommendations.
"""
        
        return enhanced_prompt.strip()
    
    def _format_response_with_citations(self, response: str, enhanced_query: RAGEnhancedQuery) -> str:
        """Format response with RAG citations."""
        formatted_response = response
        
        if enhanced_query.sources:
            formatted_response += "\n\n**Sources:**\n"
            for i, source in enumerate(enhanced_query.sources[:5], 1):  # Limit to top 5 sources
                source_info = source.get('filename', 'Unknown source')
                formatted_response += f"{i}. {source_info}\n"
        
        if enhanced_query.confidence_score > 0:
            formatted_response += f"\n*Knowledge confidence: {enhanced_query.confidence_score:.1%}*"
        
        return formatted_response


class CodeImprovementOrchestrator:
    """Orchestrator for specialized code improvement using RAG-enhanced agents."""
    
    def __init__(self, agent_manager: UnifiedAgentManager, rag_system: SearchSystem):
        """
        Initialize code improvement orchestrator.
        
        Args:
            agent_manager: Unified agent system manager
            rag_system: RAG search system
        """
        self.agent_manager = agent_manager
        self.rag_system = rag_system
        self.rag_enhanced_agents = {}
        
        # Create RAG-enhanced versions of code-related agents
        self._initialize_rag_enhanced_agents()
    
    def _initialize_rag_enhanced_agents(self):
        """Initialize RAG-enhanced versions of relevant agents."""
        code_agent_types = [
            AgentType.CODE_ANALYZER,
            AgentType.CODE_DEBUGGER,
            AgentType.CODE_REPAIR,
            AgentType.PERFORMANCE,
            AgentType.TEST_GENERATOR,
            AgentType.CEO,  # For high-level code architecture decisions
            AgentType.RESEARCH  # For research-based code improvements
        ]
        
        for agent_type in code_agent_types:
            if agent_type in self.agent_manager.agents:
                base_agent = self.agent_manager.agents[agent_type]
                enhanced_agent = RAGEnhancedAgent(base_agent, self.rag_system, agent_type)
                self.rag_enhanced_agents[agent_type] = enhanced_agent
                print(f"✅ Created RAG-enhanced {agent_type.value} agent")
    
    async def analyze_code(self, code: str, analysis_type: str = "general", 
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze code using RAG-enhanced agents.
        
        Args:
            code: Code to analyze
            analysis_type: Type of analysis (general, performance, security, etc.)
            context: Additional context
            
        Returns:
            Comprehensive code analysis with RAG-enhanced insights
        """
        start_time = time.time()
        
        # Select appropriate agent based on analysis type
        agent_type_mapping = {
            "general": AgentType.CODE_ANALYZER,
            "performance": AgentType.PERFORMANCE,
            "debugging": AgentType.CODE_DEBUGGER,
            "security": AgentType.CEO,
            "testing": AgentType.TEST_GENERATOR
        }
        
        agent_type = agent_type_mapping.get(analysis_type, AgentType.CODE_ANALYZER)
        
        if agent_type not in self.rag_enhanced_agents:
            return {
                "success": False,
                "error": f"RAG-enhanced agent not available for {analysis_type}"
            }
        
        try:
            enhanced_agent = self.rag_enhanced_agents[agent_type]
            
            # Create analysis query
            query = f"Analyze this code and provide insights:\n\n```\n{code}\n```"
            
            # Run RAG-enhanced analysis
            analysis_result = enhanced_agent.run(query, context)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "analysis_type": analysis_type,
                "agent_used": enhanced_agent.name,
                "result": analysis_result,
                "execution_time": execution_time,
                "timestamp": time.time()
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": time.time()
            }
    
    async def improve_code(self, code: str, improvement_type: str = "general",
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Improve code using RAG-enhanced agents.
        
        Args:
            code: Code to improve
            improvement_type: Type of improvement (general, performance, debugging, repair)
            context: Additional context
            
        Returns:
            Code improvements with RAG-enhanced recommendations
        """
        start_time = time.time()
        
        # Select appropriate agent based on improvement type
        agent_type_mapping = {
            "general": AgentType.CODE_ANALYZER,
            "performance": AgentType.PERFORMANCE,
            "debugging": AgentType.CODE_DEBUGGER,
            "repair": AgentType.CODE_REPAIR
        }
        
        agent_type = agent_type_mapping.get(improvement_type, AgentType.CODE_ANALYZER)
        
        if agent_type not in self.rag_enhanced_agents:
            return {
                "success": False,
                "error": f"RAG-enhanced agent not available for {improvement_type}"
            }
        
        try:
            enhanced_agent = self.rag_enhanced_agents[agent_type]
            
            # Create improvement query
            query = f"Provide code improvements and recommendations for:\n\n```\n{code}\n```"
            
            # Run RAG-enhanced improvement
            improvement_result = enhanced_agent.run(query, context)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "improvement_type": improvement_type,
                "agent_used": enhanced_agent.name,
                "result": improvement_result,
                "execution_time": execution_time,
                "timestamp": time.time()
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": time.time()
            }
    
    async def query_coding_knowledge(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query coding knowledge using RAG-enhanced research agent.
        
        Args:
            query: Knowledge query
            context: Additional context
            
        Returns:
            Knowledge-based response with RAG context
        """
        start_time = time.time()
        
        if AgentType.RESEARCH not in self.rag_enhanced_agents:
            return {
                "success": False,
                "error": "RAG-enhanced research agent not available"
            }
        
        try:
            research_agent = self.rag_enhanced_agents[AgentType.RESEARCH]
            
            # Run RAG-enhanced knowledge query
            knowledge_result = research_agent.run(query, context)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "query": query,
                "agent_used": research_agent.name,
                "result": knowledge_result,
                "execution_time": execution_time,
                "timestamp": time.time()
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": time.time()
            }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of RAG-enhanced agents."""
        status = {
            "total_rag_enhanced_agents": len(self.rag_enhanced_agents),
            "rag_system_available": self.rag_system is not None,
            "agents": {}
        }
        
        for agent_type, agent in self.rag_enhanced_agents.items():
            status["agents"][agent_type.value] = {
                "name": agent.name,
                "base_agent": type(agent.base_agent).__name__,
                "specializations": [spec.value for spec in agent.rag_specializations.get(agent_type, [])],
                "status": "ready"
            }
        
        return status


def integrate_rag_with_agents(agent_manager: UnifiedAgentManager, rag_system: SearchSystem) -> CodeImprovementOrchestrator:
    """
    Integrate RAG system with unified agent system for enhanced code improvement.
    
    Args:
        agent_manager: Unified agent system manager
        rag_system: RAG search system
        
    Returns:
        Code improvement orchestrator with RAG-enhanced agents
    """
    orchestrator = CodeImprovementOrchestrator(agent_manager, rag_system)
    print("✅ RAG-Agent integration completed successfully")
    print(f"🔗 {len(orchestrator.rag_enhanced_agents)} agents enhanced with RAG capabilities")
    return orchestrator


# Export main classes and functions
__all__ = [
    'RAGEnhancedAgent', 'CodeImprovementOrchestrator', 'RAGQueryType', 'RAGEnhancedQuery',
    'integrate_rag_with_agents'
]
