"""
Agent Classes for the Unified Agent System
Contains all specialized agents for code analysis, debugging, performance optimization, and more.
Uses Ollama for local LLM inference.
"""

import os
import asyncio
import time
import json
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

# Try to import Ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
    
    # Test connection to Ollama
    try:
        ollama.list()
        logger.info("✅ Ollama client initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ Ollama connection issue: {e}")
        OLLAMA_AVAILABLE = False
        
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None
    logger.warning("⚠️ Ollama not installed")

class AgentCapability(Enum):
    """Agent capability types."""
    CODE_ANALYSIS = "code_analysis"
    CODE_DEBUGGING = "code_debugging"
    CODE_REPAIR = "code_repair"
    PERFORMANCE_PROFILING = "performance_profiling"
    TEST_GENERATION = "test_generation"
    IMAGE_PROCESSING = "image_processing"
    AUDIO_PROCESSING = "audio_processing"
    EXECUTION = "execution"
    COORDINATION = "coordination"

@dataclass
class AgentResponse:
    """Response from an agent."""
    success: bool
    result: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None

class Agent(ABC):
    """Base agent class with common functionality."""
    
    def __init__(self, name: str, model: str = "phi3.5", capabilities: Optional[List[AgentCapability]] = None):
        self.name = name
        self.model = model
        self.capabilities = capabilities or []
        self.conversation_history = []
        self.created_at = time.time()
        self.total_executions = 0
        self.successful_executions = 0
        
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Execute a task and return the response."""
        pass
    
    def add_capability(self, capability: AgentCapability):
        """Add a capability to the agent."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability."""
        return capability in self.capabilities
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        success_rate = (self.successful_executions / self.total_executions * 100) if self.total_executions > 0 else 0
        return {
            "name": self.name,
            "model": self.model,
            "capabilities": [cap.value for cap in self.capabilities],
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "success_rate": round(success_rate, 2),
            "uptime": time.time() - self.created_at
        }
    
    async def _call_ollama(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Call Ollama API with error handling."""
        try:
            if not OLLAMA_AVAILABLE or not ollama:
                return f"Ollama not available - {self.name} agent returning mock response"
            
            # Convert messages to a single prompt for Ollama
            prompt = self._messages_to_prompt(messages)
            
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': temperature,
                    'num_predict': 1000  # Max tokens
                }
            )
            
            return response['response']
            
        except Exception as e:
            logger.error(f"Ollama API call failed for {self.name}: {e}")
            return f"Error calling Ollama: {str(e)}"
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to a single prompt for Ollama."""
        prompt_parts = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"System: {content}\n")
            elif role == 'user':
                prompt_parts.append(f"User: {content}\n")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}\n")
        
        prompt_parts.append("Assistant: ")
        return '\n'.join(prompt_parts)

class ExecutorWithFallback(Agent):
    """Executor agent with fallback capabilities."""
    
    def __init__(self, name: str = "ExecutorAgent", model: str = "phi3.5"):
        super().__init__(name, model, [AgentCapability.EXECUTION])
        self.fallback_model = "llama2"
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Execute a task with fallback support."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            # Primary execution attempt
            result = await self._execute_task(task)
            self.successful_executions += 1
            
            return AgentResponse(
                success=True,
                result=result,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.warning(f"Primary execution failed for {self.name}, trying fallback: {e}")
            
            try:
                # Fallback execution
                original_model = self.model
                self.model = self.fallback_model
                result = await self._execute_task(task)
                self.model = original_model
                self.successful_executions += 1
                
                return AgentResponse(
                    success=True,
                    result=result,
                    metadata={"used_fallback": True},
                    execution_time=time.time() - start_time
                )
                
            except Exception as fallback_error:
                self.model = original_model
                return AgentResponse(
                    success=False,
                    result=None,
                    error=f"Both primary and fallback execution failed: {str(e)}, {str(fallback_error)}",
                    execution_time=time.time() - start_time
                )
    
    async def _execute_task(self, task: Dict[str, Any]) -> str:
        """Execute the actual task."""
        task_type = task.get("type", "general")
        content = task.get("content", "")
        
        messages = [
            {"role": "system", "content": f"You are an expert executor agent. Execute the following {task_type} task efficiently and accurately."},
            {"role": "user", "content": content}
        ]
        
        return await self._call_ollama(messages)

class CodeAnalyzerAgent(Agent):
    """Agent specialized in code analysis."""
    
    def __init__(self, name: str = "CodeAnalyzer", model: str = "codellama"):
        super().__init__(name, model, [AgentCapability.CODE_ANALYSIS])
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Analyze code and provide insights."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            code = task.get("code", "")
            analysis_type = task.get("analysis_type", "general")
            
            system_prompt = """You are an expert code analyzer. Analyze the provided code and provide:
1. Code quality assessment
2. Potential bugs or issues
3. Performance considerations
4. Best practices recommendations
5. Security vulnerabilities if any
6. Maintainability score (1-10)

Provide your analysis in a structured format."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this {analysis_type} code:\n\n{code}"}
            ]
            
            result = await self._call_ollama(messages, temperature=0.3)
            self.successful_executions += 1
            
            return AgentResponse(
                success=True,
                result=result,
                metadata={"analysis_type": analysis_type},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                result=None,
                error=str(e),
                execution_time=time.time() - start_time
            )

class CodeDebuggerAgent(Agent):
    """Agent specialized in debugging code."""
    
    def __init__(self, name: str = "CodeDebugger", model: str = "codellama"):
        super().__init__(name, model, [AgentCapability.CODE_DEBUGGING])
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Debug code and identify issues."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            code = task.get("code", "")
            error_message = task.get("error_message", "")
            
            system_prompt = """You are an expert debugging agent. For the provided code and error:
1. Identify the root cause of the issue
2. Explain why the error occurs
3. Provide step-by-step debugging approach
4. Suggest multiple solution approaches
5. Highlight preventive measures for similar issues

Format your response as a structured debugging report."""

            user_content = f"Debug this code:\n\n{code}"
            if error_message:
                user_content += f"\n\nError message: {error_message}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
            
            result = await self._call_ollama(messages, temperature=0.2)
            self.successful_executions += 1
            
            return AgentResponse(
                success=True,
                result=result,
                metadata={"has_error_message": bool(error_message)},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                result=None,
                error=str(e),
                execution_time=time.time() - start_time
            )

class CodeRepairAgent(Agent):
    """Agent specialized in repairing and fixing code."""
    
    def __init__(self, name: str = "CodeRepairer", model: str = "codellama"):
        super().__init__(name, model, [AgentCapability.CODE_REPAIR])
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Repair and fix code issues."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            code = task.get("code", "")
            issues = task.get("issues", "")
            repair_type = task.get("repair_type", "general")
            
            system_prompt = """You are an expert code repair agent. For the provided code:
1. Fix all identified issues and bugs
2. Improve code quality and readability
3. Optimize performance where possible
4. Ensure best practices are followed
5. Add necessary comments and documentation
6. Provide the corrected code with explanations

Return both the fixed code and detailed explanation of changes made."""

            user_content = f"Repair this {repair_type} code:\n\n{code}"
            if issues:
                user_content += f"\n\nKnown issues: {issues}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
            
            result = await self._call_ollama(messages, temperature=0.3)
            self.successful_executions += 1
            
            return AgentResponse(
                success=True,
                result=result,
                metadata={"repair_type": repair_type},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                result=None,
                error=str(e),
                execution_time=time.time() - start_time
            )

class PerformanceProfilerAgent(Agent):
    """Agent specialized in performance analysis and optimization."""
    
    def __init__(self, name: str = "PerformanceProfiler", model: str = "phi3.5"):
        super().__init__(name, model, [AgentCapability.PERFORMANCE_PROFILING])
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Analyze and optimize code performance."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            code = task.get("code", "")
            language = task.get("language", "python")
            focus_area = task.get("focus_area", "general")
            
            system_prompt = """You are an expert performance profiler. Analyze the code for:
1. Time complexity analysis
2. Space complexity analysis
3. Performance bottlenecks identification
4. Memory usage optimization opportunities
5. Algorithm efficiency improvements
6. Platform-specific optimizations
7. Caching opportunities
8. Parallelization possibilities

Provide specific, actionable optimization recommendations with code examples."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Profile this {language} code (focus: {focus_area}):\n\n{code}"}
            ]
            
            result = await self._call_ollama(messages, temperature=0.4)
            self.successful_executions += 1
            
            return AgentResponse(
                success=True,
                result=result,
                metadata={"language": language, "focus_area": focus_area},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                result=None,
                error=str(e),
                execution_time=time.time() - start_time
            )

class TestGeneratorAgent(Agent):
    """Agent specialized in generating tests."""
    
    def __init__(self, name: str = "TestGenerator", model: str = "codellama"):
        super().__init__(name, model, [AgentCapability.TEST_GENERATION])
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Generate comprehensive tests for code."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            code = task.get("code", "")
            test_type = task.get("test_type", "unit")
            framework = task.get("framework", "pytest")
            
            system_prompt = """You are an expert test generation agent. Create comprehensive tests including:
1. Unit tests for individual functions/methods
2. Integration tests for component interactions
3. Edge case testing
4. Error condition testing
5. Performance testing scenarios
6. Mock and fixture setups
7. Test data generation
8. Coverage analysis recommendations

Generate complete, runnable test code with proper setup and teardown."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate {test_type} tests using {framework} for:\n\n{code}"}
            ]
            
            result = await self._call_ollama(messages, temperature=0.5)
            self.successful_executions += 1
            
            return AgentResponse(
                success=True,
                result=result,
                metadata={"test_type": test_type, "framework": framework},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                result=None,
                error=str(e),
                execution_time=time.time() - start_time
            )

class ImageAgent(Agent):
    """Agent specialized in image processing and analysis."""
    
    def __init__(self, name: str = "ImageProcessor", model: str = "llama2"):
        super().__init__(name, model, [AgentCapability.IMAGE_PROCESSING])
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Process and analyze images."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            # For now, return a placeholder response
            # In a full implementation, this would handle image processing
            task_type = task.get("type", "analysis")
            
            result = {
                "status": "Image processing capability available",
                "task_type": task_type,
                "note": "Full image processing implementation would integrate with vision models via Ollama"
            }
            
            self.successful_executions += 1
            
            return AgentResponse(
                success=True,
                result=result,
                metadata={"task_type": task_type},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                result=None,
                error=str(e),
                execution_time=time.time() - start_time
            )

class AudioAgent(Agent):
    """Agent specialized in audio processing and analysis."""
    
    def __init__(self, name: str = "AudioProcessor", model: str = "llama2"):
        super().__init__(name, model, [AgentCapability.AUDIO_PROCESSING])
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Process and analyze audio."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            # For now, return a placeholder response
            # In a full implementation, this would handle audio processing
            task_type = task.get("type", "transcription")
            
            result = {
                "status": "Audio processing capability available",
                "task_type": task_type,
                "note": "Full audio processing implementation would integrate with audio models via Ollama"
            }
            
            self.successful_executions += 1
            
            return AgentResponse(
                success=True,
                result=result,
                metadata={"task_type": task_type},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                result=None,
                error=str(e),
                execution_time=time.time() - start_time
            )

# Additional agent classes for the unified system

class CEOAgent(Agent):
    """Chief Executive Officer agent for high-level coordination."""
    
    def __init__(self, name: str = "ChiefExecutiveOfficer", model: str = "phi3.5"):
        super().__init__(name, model, [AgentCapability.COORDINATION])
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Execute high-level coordination tasks."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            content = task.get("content", "")
            
            system_prompt = """You are the Chief Executive Officer agent responsible for:
1. High-level strategic coordination
2. Task delegation and orchestration
3. Quality assurance and oversight
4. Performance optimization
5. Resource allocation decisions

Provide executive-level guidance and coordination."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
            
            result = await self._call_ollama(messages, temperature=0.4)
            self.successful_executions += 1
            
            return AgentResponse(
                success=True,
                result=result,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                result=None,
                error=str(e),
                execution_time=time.time() - start_time
            )

class TriageAgent(Agent):
    """Triage agent for analyzing and routing requests."""
    
    def __init__(self, name: str = "TriageSpecialist", model: str = "phi3.5"):
        super().__init__(name, model, [AgentCapability.COORDINATION])
        self.routing_rules = {
            "code": ["code_analyzer", "code_debugger", "code_repair"],
            "debug": ["code_debugger", "code_repair"],
            "test": ["test_generator"],
            "performance": ["performance_profiler"],
            "image": ["image"],
            "audio": ["audio"],
            "analyze": ["code_analyzer"],
            "fix": ["code_repair"],
            "optimize": ["performance_profiler"]
        }
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Execute triage and routing analysis."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            query = task.get("content", "")
            
            # Analyze query for routing
            analysis = self.analyze_request(query)
            
            result = {
                "recommended_agent": analysis["agent_type"],
                "complexity": analysis["complexity"],
                "routing_rationale": analysis["rationale"],
                "estimated_effort": analysis["effort"]
            }
            
            self.successful_executions += 1
            
            return AgentResponse(
                success=True,
                result=result,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                result=None,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def analyze_request(self, query: str) -> Dict[str, Any]:
        """Analyze request and determine routing."""
        query_lower = query.lower()
        
        # Determine best agent type
        agent_type = "executor"  # default
        rationale = "General execution task"
        
        for keyword, agents in self.routing_rules.items():
            if keyword in query_lower:
                agent_type = agents[0]
                rationale = f"Detected '{keyword}' keyword, routing to {agent_type}"
                break
        
        # Determine complexity
        complexity = "medium"
        if len(query.split()) > 50 or any(word in query_lower for word in ["complex", "advanced", "detailed"]):
            complexity = "high"
        elif len(query.split()) < 10:
            complexity = "low"
        
        # Estimate effort
        effort_map = {"low": "1-5 minutes", "medium": "5-15 minutes", "high": "15+ minutes"}
        
        return {
            "agent_type": agent_type,
            "complexity": complexity,
            "rationale": rationale,
            "effort": effort_map[complexity]
        }

class ResearchAgent(Agent):
    """Research analyst agent for information gathering."""
    
    def __init__(self, name: str = "ResearchAnalyst", model: str = "phi3.5"):
        super().__init__(name, model, [AgentCapability.CODE_ANALYSIS])
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Execute research and analysis tasks."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            content = task.get("content", "")
            
            system_prompt = """You are a research analyst agent specialized in:
1. Information gathering and synthesis
2. Technical research and analysis
3. Market and technology trend analysis
4. Documentation and knowledge compilation
5. Data-driven insights and recommendations

Provide thorough, well-researched analysis."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
            
            result = await self._call_ollama(messages, temperature=0.5)
            self.successful_executions += 1
            
            return AgentResponse(
                success=True,
                result=result,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                result=None,
                error=str(e),
                execution_time=time.time() - start_time
            )

class CoachingAgent(Agent):
    """AI coaching agent for guidance and learning."""
    
    def __init__(self, name: str = "AICoach", model: str = "phi3.5"):
        super().__init__(name, model, [AgentCapability.COORDINATION])
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Execute coaching and guidance tasks."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            content = task.get("content", "")
            
            system_prompt = """You are an AI coaching agent focused on:
1. Personalized learning and development guidance
2. Skill assessment and improvement recommendations
3. Best practices and methodology coaching
4. Problem-solving approach guidance
5. Performance improvement strategies

Provide supportive, actionable coaching advice."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
            
            result = await self._call_ollama(messages, temperature=0.6)
            self.successful_executions += 1
            
            return AgentResponse(
                success=True,
                result=result,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                result=None,
                error=str(e),
                execution_time=time.time() - start_time
            )

# Factory function to create agents
def create_agent(agent_type: str, **kwargs) -> Agent:
    """Factory function to create agents by type."""
    agent_map = {
        "ceo": CEOAgent,
        "executor": ExecutorWithFallback,
        "triage": TriageAgent,
        "research": ResearchAgent,
        "coaching": CoachingAgent,
        "code_analyzer": CodeAnalyzerAgent,
        "code_debugger": CodeDebuggerAgent,
        "code_repair": CodeRepairAgent,
        "performance_profiler": PerformanceProfilerAgent,
        "test_generator": TestGeneratorAgent,
        "image": ImageAgent,
        "audio": AudioAgent,
    }
    
    agent_class = agent_map.get(agent_type.lower())
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return agent_class(**kwargs)

# Export all agent classes
__all__ = [
    "Agent",
    "ExecutorWithFallback", 
    "CodeAnalyzerAgent",
    "CodeDebuggerAgent", 
    "CodeRepairAgent",
    "PerformanceProfilerAgent",
    "TestGeneratorAgent",
    "ImageAgent",
    "AudioAgent",
    "CEOAgent",
    "TriageAgent",
    "ResearchAgent",
    "CoachingAgent",
    "AgentResponse",
    "AgentCapability",
    "create_agent"
]
