"""
Enhanced Agent Factory implementation for VectorDBRAG.
Creates and manages agents using the shared MindMeld framework.
"""

from typing import Dict, Any, Optional
import os

from shared_agents.core.agent_factory import AgentFactory, AgentCapability

from .enhanced_agents import (
    CEOAgent,
    ResearchAgent,
    CodeAnalysisAgent,
    CodeDebuggerAgent,
    CodeRepairAgent,
    PerformanceProfilerAgent,
    TestGeneratorAgent,
    ImageAgent,
    AudioAgent,
    TriageAgent
)

# Import the OpenAI client from original VectorDBRAG setup
try:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
    else:
        client = None
        print("Warning: OPENAI_API_KEY not found in environment variables")
except ImportError:
    client = None
    print("Warning: OpenAI library not installed")


class EnhancedAgentFactory:
    """
    Factory for creating enhanced VectorDBRAG agents using the shared framework.
    Provides access to all agent types with consistent configuration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the enhanced agent factory.
        
        Args:
            config: Optional configuration dictionary for agents
        """
        self.config = config or {}
        self.factory = AgentFactory()
        
        # Set default OpenAI client if not provided
        if 'openai_client' not in self.config:
            self.config['openai_client'] = client
        
        # Register all agent types
        self.register_default_agents()
    
    def register_default_agents(self) -> None:
        """Register all default enhanced agents."""
        # Strategic agents
        self.factory.register_agent("ceo", CEOAgent)
        self.factory.register_agent("triage", TriageAgent)
        
        # Code agents
        self.factory.register_agent("code_analysis", CodeAnalysisAgent)
        self.factory.register_agent("code_debugger", CodeDebuggerAgent)
        self.factory.register_agent("code_repair", CodeRepairAgent)
        self.factory.register_agent("performance_profiler", PerformanceProfilerAgent)
        self.factory.register_agent("test_generator", TestGeneratorAgent)
        
        # Specialized agents
        self.factory.register_agent("research", ResearchAgent)
        self.factory.register_agent("image", ImageAgent)
        self.factory.register_agent("audio", AudioAgent)
    
    def create_agent(self, agent_type: str, name: Optional[str] = None,
                     config: Optional[Dict[str, Any]] = None) -> Any:
        """
        Create an agent instance of the specified type.
        
        Args:
            agent_type: Type of agent to create
            name: Optional name for the agent
            config: Optional additional configuration
            
        Returns:
            Instance of the requested agent
        """
        # Merge configs, with provided config taking precedence
        merged_config = {**self.config}
        if config:
            merged_config.update(config)

        # Set the agent name in config, defaulting to a generated name
        merged_config["name"] = name or f"{agent_type.capitalize()}Agent"
        # Ensure default model is set for agents requiring 'model'
        if "model" not in merged_config and "default_model" in merged_config:
            merged_config["model"] = merged_config.get("default_model")

        return self.factory.create_agent(agent_type, merged_config)
    
    def get_agent_types(self) -> Dict[str, Any]:
        """Get all registered agent types and their capabilities."""
        return self.factory.get_agent_info()
    
    def create_all_agents(self) -> Dict[str, Any]:
        """
        Create instances of all registered agent types.

        Returns:
            Dictionary mapping agent type to agent instance
        """
        agents = {}
        for agent_type in self.get_agent_types().keys():
            agents[agent_type] = self.create_agent(agent_type)
        return agents
    
    def create_agents_with_capability(self, capability: AgentCapability) -> Dict[str, Any]:
        """
        Create instances of all agents with a specific capability.

        Args:
            capability: The capability to filter agents by

        Returns:
            Dictionary mapping agent type to agent instance
        """
        agents = {}
        for agent_type in self.get_agent_types().keys():
            agent = self.create_agent(agent_type)
            if agent.has_capability(capability):
                agents[agent_type] = agent
        return agents


# Create default factory instance for easy importing
default_factory = EnhancedAgentFactory()
