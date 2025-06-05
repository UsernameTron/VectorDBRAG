"""
Agent Classes for the Unified Agent System
Contains all specialized agents for code analysis, debugging, performance optimization, and more.
Uses OpenAI API for AI capabilities.
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

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI library not available. Install with: pip install openai")

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client if available
client = None
if OPENAI_AVAILABLE:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
    else:
        logger.warning("OPENAI_API_KEY not found in environment variables")

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
    
    def __init__(self, name: str, model: str = "gpt-4", capabilities: Optional[List[AgentCapability]] = None):
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
    
    async def _call_openai(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Call OpenAI API with error handling."""
        if not client:
            raise Exception("OpenAI client not initialized. Check API key and installation.")
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API call failed for {self.name}: {e}")
            raise

class ExecutorWithFallback(Agent):
    """Executor agent with fallback capabilities."""
    
    def __init__(self, name: str = "ExecutorAgent", model: str = "gpt-4"):
        super().__init__(name, model, [AgentCapability.EXECUTION])
        self.fallback_model = "gpt-3.5-turbo"
    
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
        
        return await self._call_openai(messages)
    
    def run(self, query: str) -> str:
        """Execute a query synchronously with fallback support."""
        if not client:
            return "❌ OpenAI API not available for execution operations."
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert executor agent. Execute tasks efficiently and accurately with comprehensive solutions."},
                    {"role": "user", "content": query}
                ],
                max_tokens=1500,
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            # Try fallback model
            try:
                response = client.chat.completions.create(
                    model=self.fallback_model,
                    messages=[
                        {"role": "system", "content": "You are an expert executor agent. Execute tasks efficiently and accurately with comprehensive solutions."},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=1500,
                    temperature=0.4
                )
                return response.choices[0].message.content + " (using fallback model)"
            except Exception as fallback_error:
                return f"❌ Executor processing error: Primary: {str(e)}, Fallback: {str(fallback_error)}"

class CodeAnalyzerAgent(Agent):
    """Agent specialized in code analysis."""
    
    def __init__(self, name: str = "CodeAnalyzer", model: str = "gpt-4"):
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

Provide your analysis in a structured JSON format."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this {analysis_type} code:\n\n{code}"}
            ]
            
            result = await self._call_openai(messages, temperature=0.3)
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
    
    def run(self, query: str) -> str:
        """Analyze code and provide insights."""
        if not client:
            return "❌ OpenAI API not available for code analysis."
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """You are an expert code analyzer. Analyze the provided code and provide:
1. Code quality assessment
2. Potential bugs or issues
3. Performance considerations
4. Best practices recommendations
5. Security vulnerabilities if any
6. Maintainability score (1-10)
Provide your analysis in a structured format with clear explanations."""},
                    {"role": "user", "content": query}
                ],
                max_tokens=1200,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Code analysis error: {str(e)}"

class CodeDebuggerAgent(Agent):
    """Agent specialized in debugging code."""
    
    def __init__(self, name: str = "CodeDebugger", model: str = "gpt-4"):
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

Format your response as structured debugging report."""

            user_content = f"Debug this code:\n\n{code}"
            if error_message:
                user_content += f"\n\nError message: {error_message}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
            
            result = await self._call_openai(messages, temperature=0.2)
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
    
    def run(self, query: str) -> str:
        """Synchronous interface for code debugging queries."""
        if not client:
            return "OpenAI client not available. Please check API key configuration."
        
        try:
            system_prompt = """You are an expert debugging agent. Help identify and solve code issues.
Provide step-by-step debugging guidance, root cause analysis, and solution recommendations."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Debug analysis failed: {str(e)}"

class CodeRepairAgent(Agent):
    """Agent specialized in repairing and fixing code."""
    
    def __init__(self, name: str = "CodeRepairer", model: str = "gpt-4"):
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
            
            result = await self._call_openai(messages, temperature=0.3)
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
    
    def run(self, query: str) -> str:
        """Synchronous interface for code repair queries."""
        if not client:
            return "OpenAI client not available. Please check API key configuration."
        
        try:
            system_prompt = """You are an expert code repair agent. Help fix code issues and improve code quality.
Provide corrected code with detailed explanations of changes made."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Code repair failed: {str(e)}"

class PerformanceProfilerAgent(Agent):
    """Agent specialized in performance analysis and optimization."""
    
    def __init__(self, name: str = "PerformanceProfiler", model: str = "gpt-4"):
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
            
            result = await self._call_openai(messages, temperature=0.4)
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
    
    def run(self, query: str) -> str:
        """Synchronous interface for performance analysis queries."""
        if not client:
            return "OpenAI client not available. Please check API key configuration."
        
        try:
            system_prompt = """You are an expert performance profiler. Analyze code performance and provide optimization recommendations.
Focus on time/space complexity, bottlenecks, and actionable improvements."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Performance analysis failed: {str(e)}"

class TestGeneratorAgent(Agent):
    """Agent specialized in generating tests."""
    
    def __init__(self, name: str = "TestGenerator", model: str = "gpt-4"):
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
            
            result = await self._call_openai(messages, temperature=0.5)
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
    
    def run(self, query: str) -> str:
        """Synchronous interface for test generation queries."""
        if not client:
            return "OpenAI client not available. Please check API key configuration."
        
        try:
            system_prompt = """You are an expert test generation agent. Create comprehensive tests for code.
Generate unit tests, integration tests, edge cases, and provide complete runnable test code."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Test generation failed: {str(e)}"

class ImageAgent(Agent):
    """Agent specialized in image processing and analysis."""
    
    def __init__(self, name: str = "ImageProcessor", model: str = "gpt-4-vision-preview"):
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
                "note": "Full image processing implementation would integrate with vision models"
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
    
    def run(self, query: str) -> str:
        """Synchronous interface for image analysis queries."""
        if not client:
            return "OpenAI client not available. Please check API key configuration."
        
        try:
            system_prompt = """You are an expert image analysis agent. Help with image processing tasks and visual content analysis.
Provide guidance on image processing techniques, computer vision approaches, and visual analysis."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.6
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Image analysis failed: {str(e)}"

class AudioAgent(Agent):
    """Agent specialized in audio processing tasks."""
    
    def __init__(self, name: str = "Audio Agent", model: str = "gpt-4"):
        super().__init__(name, model)
        self.capabilities = [AgentCapability.AUDIO_PROCESSING]
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Execute audio processing tasks."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            result = await self._call_openai([
                {"role": "system", "content": """You are an expert audio processing specialist. You help with:
                - Audio analysis and manipulation
                - Audio format conversion
                - Sound quality improvement
                - audio transcription and processing
                - Music and speech analysis
                Provide practical solutions and code examples when appropriate."""},
                {"role": "user", "content": task.get("content", "")}
            ])
            
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
    
    def run(self, query: str) -> str:
        """Process audio-related queries."""
        if not client:
            return "❌ OpenAI API not available for audio processing."
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """You are an expert audio processing specialist. You help with:
                    - Audio analysis and manipulation
                    - Audio format conversion
                    - Sound quality improvement
                    - Audio transcription and processing
                    - Music and speech analysis
                    Provide practical solutions and code examples when appropriate."""},
                    {"role": "user", "content": query}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Audio processing error: {str(e)}"


class CEOAgent(Agent):
    """Chief Executive Officer Agent - Handles complex strategic decisions and coordination."""
    
    def __init__(self, name: str = "Chief Executive Officer", model: str = "gpt-4"):
        super().__init__(name, model)
        self.capabilities = [AgentCapability.COORDINATION, AgentCapability.EXECUTION]
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Execute strategic and coordination tasks."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            result = await self._call_openai([
                {"role": "system", "content": """You are the Chief Executive Officer agent, responsible for:
                - High-level strategic planning and decision-making
                - Complex problem solving and coordination
                - Multi-faceted project management
                - Resource allocation and optimization
                - Executive-level analysis and recommendations
                - Coordinating between different specialized agents
                Provide comprehensive, strategic solutions with clear action plans."""},
                {"role": "user", "content": task.get("content", "")}
            ])
            
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
    
    def run(self, query: str) -> str:
        """Handle complex strategic and coordination tasks."""
        if not client:
            return "❌ OpenAI API not available for CEO operations."
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """You are the Chief Executive Officer agent, responsible for:
                    - High-level strategic planning and decision-making
                    - Complex problem solving and coordination
                    - Multi-faceted project management
                    - Resource allocation and optimization
                    - Executive-level analysis and recommendations
                    - Coordinating between different specialized agents
                    Provide comprehensive, strategic solutions with clear action plans."""},
                    {"role": "user", "content": query}
                ],
                max_tokens=1500,
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ CEO processing error: {str(e)}"


class TriageAgent(Agent):
    """Triage Agent - Routes requests to appropriate specialized agents."""
    
    def __init__(self, name: str = "Triage Specialist", model: str = "gpt-3.5-turbo"):
        super().__init__(name, model)
        self.capabilities = [AgentCapability.COORDINATION]
        self.routing_rules = {
            "code": ["code_analyzer", "code_debugger", "code_repair"],
            "debug": ["code_debugger", "test_generator"],
            "performance": ["performance", "code_analyzer"],
            "research": ["research", "ceo"],
            "image": ["image"],
            "audio": ["audio"],
            "test": ["test_generator"],
            "coach": ["coaching"],
            "complex": ["ceo", "executor"]
        }
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Execute triage and routing tasks."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            result = await self._call_openai([
                {"role": "system", "content": """You are a triage specialist responsible for:
                - Analyzing incoming requests and determining urgency
                - Routing tasks to the most appropriate specialist
                - Breaking down complex problems into manageable components
                - Providing initial assessment and recommendations
                - Coordinating multi-agent workflows
                Provide clear analysis and routing recommendations."""},
                {"role": "user", "content": task.get("content", "")}
            ])
            
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
    
    def analyze_request(self, query: str, context: Optional[Dict[str, Any]] = None):
        """Analyze request and determine appropriate routing."""
        query_lower = query.lower()
        
        # Determine agent type based on content
        agent_type = "executor"  # default
        for keyword, agents in self.routing_rules.items():
            if keyword in query_lower:
                agent_type = agents[0]  # Primary agent for this category
                break
        
        # Determine complexity
        complexity = "medium"
        if len(query.split()) > 50 or "complex" in query_lower:
            complexity = "high"
        elif len(query.split()) < 10:
            complexity = "low"
        
        return {
            "agent_type": agent_type,
            "complexity": complexity,
            "query": query,
            "context": context or {}
        }
    
    def run(self, query: str) -> str:
        """Route and process triage requests."""
        if not client:
            return "❌ OpenAI API not available for triage operations."
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """You are a triage specialist responsible for:
                    - Analyzing incoming requests and determining urgency
                    - Routing tasks to the most appropriate specialist
                    - Breaking down complex problems into manageable components
                    - Providing initial assessment and recommendations
                    - Coordinating multi-agent workflows
                    Provide clear analysis and routing recommendations."""},
                    {"role": "user", "content": query}
                ],
                max_tokens=800,
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Triage processing error: {str(e)}"


class ResearchAgent(Agent):
    """Research Agent - Handles research, analysis, and information gathering tasks."""
    
    def __init__(self, name: str = "Research Analyst", model: str = "gpt-4"):
        super().__init__(name, model)
        self.capabilities = [AgentCapability.CODE_ANALYSIS]
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Execute research and analysis tasks."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            result = await self._call_openai([
                {"role": "system", "content": """You are a research analyst specialist responsible for:
                - Comprehensive information gathering and analysis
                - Market research and competitive analysis
                - Technical research and feasibility studies
                - Data analysis and trend identification
                - Literature reviews and documentation
                - Fact-checking and source verification
                Provide thorough, well-researched responses with citations when possible."""},
                {"role": "user", "content": task.get("content", "")}
            ])
            
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
    
    def run(self, query: str) -> str:
        """Handle research and analysis tasks."""
        if not client:
            return "❌ OpenAI API not available for research operations."
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """You are a research analyst specialist responsible for:
                    - Comprehensive information gathering and analysis
                    - Market research and competitive analysis
                    - Technical research and feasibility studies
                    - Data analysis and trend identification
                    - Literature reviews and documentation
                    - Fact-checking and source verification
                    Provide thorough, well-researched responses with citations when possible."""},
                    {"role": "user", "content": query}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Research processing error: {str(e)}"


class PerformanceAgent(Agent):
    """Performance Agent - Handles performance analysis and optimization tasks."""
    
    def __init__(self, name: str = "Performance Analyst", model: str = "gpt-4"):
        super().__init__(name, model)
        self.capabilities = [AgentCapability.PERFORMANCE_PROFILING, AgentCapability.CODE_ANALYSIS]
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Execute performance analysis and optimization tasks."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            result = await self._call_openai([
                {"role": "system", "content": """You are a performance analysis specialist responsible for:
                - Application and system performance optimization
                - Code performance profiling and analysis
                - Resource utilization analysis
                - Bottleneck identification and resolution
                - Performance benchmarking and testing
                - Scalability analysis and recommendations
                Provide detailed performance insights with specific optimization recommendations."""},
                {"role": "user", "content": task.get("content", "")}
            ])
            
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
    
    def run(self, query: str) -> str:
        """Handle performance analysis and optimization tasks."""
        if not client:
            return "❌ OpenAI API not available for performance analysis."
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """You are a performance analysis specialist responsible for:
                    - Application and system performance optimization
                    - Code performance profiling and analysis
                    - Resource utilization analysis
                    - Bottleneck identification and resolution
                    - Performance benchmarking and testing
                    - Scalability analysis and recommendations
                    Provide detailed performance insights with specific optimization recommendations."""},
                    {"role": "user", "content": query}
                ],
                max_tokens=1200,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Performance analysis error: {str(e)}"


class CoachingAgent(Agent):
    """Coaching Agent - Provides mentoring, guidance, and educational support."""
    
    def __init__(self, name: str = "AI Coach", model: str = "gpt-4"):
        super().__init__(name, model)
        self.capabilities = [AgentCapability.COORDINATION]
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Execute coaching, mentoring, and educational tasks."""
        start_time = time.time()
        self.total_executions += 1
        
        try:
            result = await self._call_openai([
                {"role": "system", "content": """You are an AI coach and mentor responsible for:
                - Providing personalized guidance and mentoring
                - Educational support and skill development
                - Career coaching and professional development
                - Learning path recommendations
                - Motivational support and encouragement
                - Goal setting and progress tracking
                - Problem-solving coaching and critical thinking development
                Provide supportive, encouraging, and actionable guidance."""},
                {"role": "user", "content": task.get("content", "")}
            ])
            
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
    
    def run(self, query: str) -> str:
        """Provide coaching, mentoring, and educational support."""
        if not client:
            return "❌ OpenAI API not available for coaching operations."
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """You are an AI coach and mentor responsible for:
                    - Providing personalized guidance and mentoring
                    - Educational support and skill development
                    - Career coaching and professional development
                    - Learning path recommendations
                    - Motivational support and encouragement
                    - Goal setting and progress tracking
                    - Problem-solving coaching and critical thinking development
                    Provide supportive, encouraging, and actionable guidance."""},
                    {"role": "user", "content": query}
                ],
                max_tokens=1200,
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Coaching error: {str(e)}"