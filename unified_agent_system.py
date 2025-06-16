"""
Unified Agent System - Integrates 12 Specialized Agents with RAG and Analytics
Combines Local O1 Multi-Agent Platform with Business Intelligence and Knowledge Management
"""

import os
import json
import time
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Local imports from existing systems
from legacy_agents import (
    Agent, ExecutorWithFallback, TestGeneratorAgent, ImageAgent, AudioAgent,
    CodeAnalyzerAgent, CodeDebuggerAgent, CodeRepairAgent, PerformanceProfilerAgent,
    CEOAgent, ResearchAgent, PerformanceAgent, CoachingAgent
)
from legacy_agents import TriageAgent as AgentTriageAgent
from config import CEO_MODEL, FAST_MODEL, EXECUTOR_MODEL_ORIGINAL, EXECUTOR_MODEL_DISTILLED
from config import CEO_MODEL, FAST_MODEL, EXECUTOR_MODEL_ORIGINAL, EXECUTOR_MODEL_DISTILLED
from vector_memory_text import vector_memory

# Try to import RAG components if available
try:
    from search_system import SearchSystem
    from integrations.analytics_integration import AnalyticsIntegration
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️  RAG system components not available in this branch")


class AgentType(Enum):
    """Enumeration of all available agent types."""
    CEO = "ceo"
    EXECUTOR = "executor"
    TRIAGE = "triage"
    RESEARCH = "research"
    PERFORMANCE = "performance"
    COACHING = "coaching"
    TEST_GENERATOR = "test_generator"
    CODE_ANALYZER = "code_analyzer"
    CODE_DEBUGGER = "code_debugger"
    CODE_REPAIR = "code_repair"
    IMAGE = "image"
    AUDIO = "audio"


class TaskComplexity(Enum):
    """Task complexity levels for intelligent routing."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentTask:
    """Structured task representation for agent processing."""
    id: str
    content: str
    agent_type: AgentType
    complexity: TaskComplexity
    context: Optional[Dict[str, Any]] = None
    priority: int = 1
    created_at: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


@dataclass
class AgentResponse:
    """Structured response from agent processing."""
    task_id: str
    agent_name: str
    result: str
    success: bool
    execution_time: float
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None





class UnifiedAgentManager:
    """Central manager for all 12 specialized agents with intelligent orchestration."""
    
    def __init__(self, rag_system=None, analytics_integration=None):
        """Initialize the unified agent system."""
        self.rag_system = rag_system
        self.analytics_integration = analytics_integration
        
        # Initialize all 12 agents with proper error handling
        self.agents = {}
        self._init_agents()
        
        self.task_queue = []
        self.active_tasks = {}
        self.completed_tasks = {}
        
        print("✅ Unified Agent System initialized with 12 specialized agents")
    
    def _init_agents(self):
        """Initialize all agents with proper error handling."""
        agent_configs = {
            AgentType.CEO: ("Chief Executive Officer", lambda: CEOAgent("Chief Executive Officer", CEO_MODEL)),
            AgentType.EXECUTOR: ("Executor", lambda: ExecutorWithFallback("Executor", EXECUTOR_MODEL_DISTILLED)),
            AgentType.TRIAGE: ("Triage Specialist", lambda: AgentTriageAgent()),
            AgentType.RESEARCH: ("Research Analyst", lambda: ResearchAgent("Research Analyst", CEO_MODEL)),
            AgentType.PERFORMANCE: ("Performance Analyst", lambda: PerformanceAgent("Performance Analyst", CEO_MODEL)),
            AgentType.COACHING: ("AI Coach", lambda: CoachingAgent("AI Coach", CEO_MODEL)),
            AgentType.TEST_GENERATOR: ("Test Generator", lambda: TestGeneratorAgent("Test Generator", CEO_MODEL)),
            AgentType.CODE_ANALYZER: ("Code Analyzer", lambda: CodeAnalyzerAgent()),
            AgentType.CODE_DEBUGGER: ("Code Debugger", lambda: CodeDebuggerAgent()),
            AgentType.CODE_REPAIR: ("Code Repair", lambda: CodeRepairAgent()),
            AgentType.IMAGE: ("Image Agent", lambda: ImageAgent()),
            AgentType.AUDIO: ("Audio Agent", lambda: AudioAgent())
        }
        
        for agent_type, (name, creator) in agent_configs.items():
            try:
                agent = creator()
                # Ensure agent has name attribute
                if not hasattr(agent, 'name'):
                    agent.name = name
                self.agents[agent_type] = agent
            except Exception as e:
                print(f"⚠️  Failed to initialize {name}: {e}")
                # Create a fallback executor agent instead of abstract Agent
                fallback = ExecutorWithFallback(name, FAST_MODEL)
                self.agents[agent_type] = fallback
    
    def process_request(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process a request through the unified agent system."""
        start_time = time.time()
        context = context or {}
        
        try:
            # Step 1: Triage and analyze request
            triage_agent = self.agents[AgentType.TRIAGE]
            triage_result = triage_agent.analyze_request(query, context)
            
            # Step 2: Convert triage result to proper AgentTask
            # Map string agent type to enum
            agent_type_str = triage_result.get("agent_type", "EXECUTOR")
            try:
                primary_agent_type = AgentType(agent_type_str.lower())
            except ValueError:
                # Fallback to executor if agent type not found
                primary_agent_type = AgentType.EXECUTOR
            
            # Map string complexity to enum
            complexity_str = triage_result.get("complexity", "MEDIUM")
            try:
                complexity = TaskComplexity(complexity_str.lower())
            except ValueError:
                complexity = TaskComplexity.MEDIUM
            
            # Create proper AgentTask object
            task = AgentTask(
                id=f"task_{int(time.time() * 1000)}",
                content=query,
                agent_type=primary_agent_type,
                complexity=complexity,
                context=context
            )
            
            primary_agent = self.agents[primary_agent_type]
            
            # Step 3: Execute task
            if hasattr(primary_agent, 'run'):
                result = primary_agent.run(query)
            elif hasattr(primary_agent, 'execute'):
                # Try async execute method
                import asyncio
                if asyncio.iscoroutinefunction(primary_agent.execute):
                    # Run async method
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        exec_response = loop.run_until_complete(primary_agent.execute({"content": query}))
                        result = exec_response.result if hasattr(exec_response, 'result') else str(exec_response)
                    finally:
                        loop.close()
                else:
                    exec_response = primary_agent.execute({"content": query})
                    result = exec_response.result if hasattr(exec_response, 'result') else str(exec_response)
            else:
                result = f"Agent {primary_agent.name} processed: {query}"
            
            execution_time = time.time() - start_time
            
            # Step 4: Create response
            response = AgentResponse(
                task_id=task.id,
                agent_name=getattr(primary_agent, 'name', str(primary_agent_type.value)),
                result=result,
                success=True,
                execution_time=execution_time,
                metadata={
                    "agent_type": primary_agent_type.value,
                    "complexity": complexity.value,
                    "triage_routing": agent_type_str
                }
            )
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            return AgentResponse(
                task_id=f"error_{int(time.time() * 1000)}",
                agent_name="System",
                result="",
                success=False,
                execution_time=execution_time,
                error=str(e)
            )
    
    def process_task(self, task: AgentTask) -> AgentResponse:
        """Process a structured AgentTask through the unified agent system."""
        start_time = time.time()
        
        try:
            # Get the appropriate agent for the task
            primary_agent = self.agents.get(task.agent_type)
            if not primary_agent:
                # Fallback to executor if specific agent not available
                primary_agent = self.agents.get(AgentType.EXECUTOR)
            
            if not primary_agent:
                raise Exception(f"No agent available for task type: {task.agent_type}")
            
            # Store task in active tasks
            self.active_tasks[task.id] = task
            
            # Execute task based on agent capabilities
            if hasattr(primary_agent, 'run'):
                result = primary_agent.run(task.content)
            elif hasattr(primary_agent, 'execute'):
                # Try async execute method
                import asyncio
                if asyncio.iscoroutinefunction(primary_agent.execute):
                    # Run async method
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        exec_response = loop.run_until_complete(primary_agent.execute({"content": task.content}))
                        result = exec_response.result if hasattr(exec_response, 'result') else str(exec_response)
                    finally:
                        loop.close()
                else:
                    exec_response = primary_agent.execute({"content": task.content})
                    result = exec_response.result if hasattr(exec_response, 'result') else str(exec_response)
            else:
                result = f"Agent {primary_agent.name} processed: {task.content}"
            
            execution_time = time.time() - start_time
            
            # Create response
            response = AgentResponse(
                task_id=task.id,
                agent_name=getattr(primary_agent, 'name', str(task.agent_type.value)),
                result=result,
                success=True,
                execution_time=execution_time,
                metadata={
                    "agent_type": task.agent_type.value,
                    "complexity": task.complexity.value,
                    "context": task.context
                }
            )
            
            # Move task to completed
            self.completed_tasks[task.id] = response
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_response = AgentResponse(
                task_id=task.id,
                agent_name="System",
                result="",
                success=False,
                execution_time=execution_time,
                error=str(e)
            )
            
            # Move task to completed with error
            self.completed_tasks[task.id] = error_response
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            
            return error_response

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents and system health."""
        status = {
            "system_status": "operational",
            "total_agents": len(self.agents),
            "agent_details": {},
            "integrations": {
                "rag_system": self.rag_system is not None,
                "analytics_integration": self.analytics_integration is not None
            },
            "memory_usage": len(vector_memory.entries) if hasattr(vector_memory, 'entries') else 0
        }
        
        for agent_type, agent in self.agents.items():
            agent_name = getattr(agent, 'name', f"Agent_{agent_type.value}")
            agent_model = getattr(agent, 'model', 'N/A')
            
            # Ensure model is JSON serializable
            if hasattr(agent_model, '__class__'):
                agent_model = agent_model.__class__.__name__ if not isinstance(agent_model, str) else agent_model
            
            status["agent_details"][agent_type.value] = {
                "name": agent_name,
                "model": str(agent_model),
                "status": "ready",
                "type": type(agent).__name__
            }
        
        return status


# Factory function
def create_unified_system(rag_system=None, analytics_integration=None) -> UnifiedAgentManager:
    """Factory function to create a unified agent system with all integrations."""
    return UnifiedAgentManager(rag_system, analytics_integration)


def quick_agent_query(query: str, agent_type: str = "auto", context: Optional[Dict[str, Any]] = None) -> str:
    """Quick utility function for single agent queries."""
    unified_system = create_unified_system()
    
    if agent_type != "auto":
        try:
            agent_enum = AgentType(agent_type)
            agent = unified_system.agents[agent_enum]
            if hasattr(agent, 'run'):
                return agent.run(query)
            else:
                return f"Agent {agent.name} processed: {query}"
        except:
            pass
    
    # Auto-route through triage
    response = unified_system.process_request(query, context)
    return response.result


# Export main classes and functions
__all__ = [
    'UnifiedAgentManager', 'AgentType', 'TaskComplexity', 'AgentTask', 'AgentResponse',
    'create_unified_system', 'quick_agent_query'
]
