"""
Enhanced agents for VectorDBRAG using the shared agent framework.
These agents inherit from the shared AgentBase and provide the functionality
from the original VectorDBRAG agents with improved validation, error handling,
and statistics tracking.
"""

import asyncio
import os
import time
from typing import Dict, Any, Optional, List

from shared_agents.core.agent_factory import (
    AgentBase, 
    AgentResponse, 
    AgentCapability, 
    AgentExecutionError,
    ValidationError
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


class CEOAgent(AgentBase):
    """
    Enhanced CEO Agent with MindMeld framework integration.
    Handles high-level strategic decisions and coordination.
    """
    
    REQUIRED_CONFIG_FIELDS = ['openai_client', 'model']
    DEFAULT_CAPABILITIES = [
        AgentCapability.STRATEGIC_PLANNING,
        AgentCapability.WORKFLOW_ORCHESTRATION
    ]
    
    def __init__(self, name: str, agent_type: str, config: Dict[str, Any]):
        super().__init__(name, agent_type, config, self.DEFAULT_CAPABILITIES)
        self.openai_client = config.get('openai_client', client)
        self.model = config.get('model', 'gpt-4')
        
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate CEO agent input."""
        required_fields = ['query']
        return all(field in input_data for field in required_fields)
        
    def validate_output(self, output_data: Any) -> bool:
        """Validate CEO agent output."""
        return output_data is not None and isinstance(output_data, str)
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Execute CEO agent strategic analysis."""
        query = input_data.get('query', '')
        if not query:
            raise ValidationError("Query is required for CEO agent")
            
        context = input_data.get('context', '')
        
        if not self.openai_client:
            raise AgentExecutionError("OpenAI client not available")
        
        try:
            messages = [
                {
                    "role": "system", 
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user", 
                    "content": f"Context: {context}\nQuery: {query}" if context else query
                }
            ]
            
            response = await self._call_openai_async(messages)
            
            return AgentResponse(
                success=True,
                result=response,
                agent_type=self.agent_type,
                timestamp=self._get_timestamp(),
                metadata={
                    "model": self.model,
                    "has_context": bool(context)
                }
            )
            
        except Exception as e:
            raise AgentExecutionError(f"CEO agent execution failed: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the CEO agent."""
        return """You are the Chief Executive Officer agent, responsible for:
        - High-level strategic planning and decision-making
        - Complex problem solving and coordination
        - Multi-faceted project management
        - Resource allocation and optimization
        - Executive-level analysis and recommendations
        - Coordinating between different specialized agents
        
        Provide comprehensive, strategic solutions with clear action plans.
        Focus on business value, feasibility, and implementation roadmaps."""
    
    async def _call_openai_async(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenAI API asynchronously."""
        loop = asyncio.get_event_loop()
        
        def _call_sync():
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=1500
            )
            return response.choices[0].message.content
        
        return await loop.run_in_executor(None, _call_sync)


class ResearchAgent(AgentBase):
    """
    Enhanced Research Agent with MindMeld framework integration.
    Handles research, analysis, and information gathering tasks.
    """
    
    REQUIRED_CONFIG_FIELDS = ['openai_client', 'model']
    DEFAULT_CAPABILITIES = [
        AgentCapability.RESEARCH,
        AgentCapability.DATA_PROCESSING,
        AgentCapability.CODE_ANALYSIS
    ]
    
    def __init__(self, name: str, agent_type: str, config: Dict[str, Any]):
        super().__init__(name, agent_type, config, self.DEFAULT_CAPABILITIES)
        self.openai_client = config.get('openai_client', client)
        self.model = config.get('model', 'gpt-4')
        
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate research agent input."""
        required_fields = ['query']
        return all(field in input_data for field in required_fields)
        
    def validate_output(self, output_data: Any) -> bool:
        """Validate research agent output."""
        return output_data is not None and isinstance(output_data, str)
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Execute research and analysis tasks."""
        query = input_data.get('query', '')
        if not query:
            raise ValidationError("Query is required for research")
            
        research_type = input_data.get('research_type', 'general')
        depth = input_data.get('depth', 'comprehensive')
        
        if not self.openai_client:
            raise AgentExecutionError("OpenAI client not available")
        
        try:
            messages = [
                {
                    "role": "system", 
                    "content": self._get_system_prompt(research_type, depth)
                },
                {
                    "role": "user", 
                    "content": query
                }
            ]
            
            response = await self._call_openai_async(messages)
            
            return AgentResponse(
                success=True,
                result=response,
                agent_type=self.agent_type,
                timestamp=self._get_timestamp(),
                metadata={
                    "model": self.model,
                    "research_type": research_type,
                    "depth": depth
                }
            )
            
        except Exception as e:
            raise AgentExecutionError(f"Research agent execution failed: {str(e)}")
    
    def _get_system_prompt(self, research_type: str, depth: str) -> str:
        """Get the system prompt for the research agent."""
        base_prompt = """You are a research analyst specialist responsible for:
        - Comprehensive information gathering and analysis
        - Market research and competitive analysis  
        - Technical research and feasibility studies
        - Data analysis and trend identification
        - Literature reviews and documentation
        - Evidence-based recommendations"""
        
        if research_type == "technical":
            base_prompt += "\n\nFocus on technical accuracy, implementation details, and engineering considerations."
        elif research_type == "market":
            base_prompt += "\n\nFocus on market trends, competitive landscape, and business implications."
        elif research_type == "academic":
            base_prompt += "\n\nFocus on scholarly sources, peer-reviewed research, and academic rigor."
            
        if depth == "comprehensive":
            base_prompt += "\n\nProvide in-depth analysis with multiple perspectives and detailed supporting evidence."
        elif depth == "summary":
            base_prompt += "\n\nProvide concise summary with key insights and actionable takeaways."
            
        return base_prompt
    
    async def _call_openai_async(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenAI API asynchronously."""
        loop = asyncio.get_event_loop()
        
        def _call_sync():
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1200
            )
            return response.choices[0].message.content
        
        return await loop.run_in_executor(None, _call_sync)


class CodeAnalysisAgent(AgentBase):
    """
    Enhanced Code Analysis Agent with MindMeld framework integration.
    Provides comprehensive code analysis and quality assessment.
    """
    
    REQUIRED_CONFIG_FIELDS = ['openai_client', 'model']
    DEFAULT_CAPABILITIES = [
        AgentCapability.CODE_ANALYSIS,
        AgentCapability.DEBUGGING,
        AgentCapability.PERFORMANCE_ANALYSIS
    ]
    
    def __init__(self, name: str, agent_type: str, config: Dict[str, Any]):
        super().__init__(name, agent_type, config, self.DEFAULT_CAPABILITIES)
        self.openai_client = config.get('openai_client', client)
        self.model = config.get('model', 'gpt-4')
        
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate code analysis agent input."""
        required_fields = ['code']
        return all(field in input_data for field in required_fields)
        
    def validate_output(self, output_data: Any) -> bool:
        """Validate code analysis agent output."""
        return output_data is not None and isinstance(output_data, str)
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Execute comprehensive code analysis."""
        code = input_data.get('code', '')
        if not code:
            raise ValidationError("Code is required for analysis")
            
        analysis_type = input_data.get('analysis_type', 'comprehensive')
        language = input_data.get('language', 'python')
        
        if not self.openai_client:
            raise AgentExecutionError("OpenAI client not available")
        
        try:
            messages = [
                {
                    "role": "system", 
                    "content": self._get_system_prompt(analysis_type, language)
                },
                {
                    "role": "user", 
                    "content": f"Analyze this {language} code:\n\n{code}"
                }
            ]
            
            response = await self._call_openai_async(messages)
            
            return AgentResponse(
                success=True,
                result=response,
                agent_type=self.agent_type,
                timestamp=self._get_timestamp(),
                metadata={
                    "model": self.model,
                    "analysis_type": analysis_type,
                    "language": language,
                    "code_length": len(code)
                }
            )
            
        except Exception as e:
            raise AgentExecutionError(f"Code analysis agent execution failed: {str(e)}")
    
    def _get_system_prompt(self, analysis_type: str, language: str) -> str:
        """Get the system prompt for the code analysis agent."""
        base_prompt = f"""You are an expert {language} code analyzer. Analyze the provided code and provide:
        1. Code quality assessment
        2. Potential bugs or issues
        3. Performance considerations
        4. Best practices recommendations
        5. Security vulnerabilities if any
        6. Maintainability score (1-10)
        7. Complexity analysis
        8. Refactoring suggestions"""
        
        if analysis_type == "security":
            base_prompt += "\n\nFocus particularly on security vulnerabilities, input validation, and secure coding practices."
        elif analysis_type == "performance":
            base_prompt += "\n\nFocus particularly on performance bottlenecks, optimization opportunities, and efficiency improvements."
        elif analysis_type == "style":
            base_prompt += "\n\nFocus particularly on code style, naming conventions, and readability improvements."
            
        base_prompt += "\n\nProvide your analysis in a structured format with clear explanations and actionable recommendations."
        
        return base_prompt
    
    async def _call_openai_async(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenAI API asynchronously."""
        loop = asyncio.get_event_loop()
        
        def _call_sync():
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1200
            )
            return response.choices[0].message.content
        
        return await loop.run_in_executor(None, _call_sync)


class TriageAgent(AgentBase):
    """
    Enhanced Triage Agent with MindMeld framework integration.
    Routes requests to appropriate specialized agents.
    """
    
    REQUIRED_CONFIG_FIELDS = ['openai_client', 'model']
    DEFAULT_CAPABILITIES = [
        AgentCapability.WORKFLOW_ORCHESTRATION
    ]
    
    def __init__(self, name: str, agent_type: str, config: Dict[str, Any]):
        super().__init__(name, agent_type, config, self.DEFAULT_CAPABILITIES)
        self.openai_client = config.get('openai_client', client)
        self.model = config.get('model', 'gpt-3.5-turbo')
        
        # Routing rules for different request types
        self.routing_rules = {
            "code": ["code_analysis", "code_debugger", "code_repair"],
            "debug": ["code_debugger", "test_generator"],
            "performance": ["performance", "code_analysis"],
            "research": ["research", "ceo"],
            "strategic": ["ceo"],
            "test": ["test_generator"],
            "complex": ["ceo", "executor"]
        }
        
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate triage agent input."""
        required_fields = ['request']
        return all(field in input_data for field in required_fields)
        
    def validate_output(self, output_data: Any) -> bool:
        """Validate triage agent output."""
        return output_data is not None and isinstance(output_data, dict)
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Execute triage and routing analysis."""
        request = input_data.get('request', '')
        if not request:
            raise ValidationError("Request is required for triage")
            
        context = input_data.get('context', {})
        
        if not self.openai_client:
            raise AgentExecutionError("OpenAI client not available")
        
        try:
            # Analyze the request to determine routing
            routing_analysis = self._analyze_request(request, context)
            
            messages = [
                {
                    "role": "system", 
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user", 
                    "content": f"Analyze and triage this request:\n\n{request}\n\nContext: {context}"
                }
            ]
            
            triage_response = await self._call_openai_async(messages)
            
            result = {
                "triage_analysis": triage_response,
                "routing_recommendation": routing_analysis,
                "priority": routing_analysis.get("priority", "medium"),
                "recommended_agents": routing_analysis.get("recommended_agents", ["executor"])
            }
            
            return AgentResponse(
                success=True,
                result=result,
                agent_type=self.agent_type,
                timestamp=self._get_timestamp(),
                metadata={
                    "model": self.model,
                    "request_length": len(request) if request else 0,
                    "has_context": bool(context)
                }
            )
            
        except Exception as e:
            raise AgentExecutionError(f"Triage agent execution failed: {str(e)}")
    
    def _analyze_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze request and determine appropriate routing."""
        request_lower = request.lower()
        
        # Determine agent type based on content
        recommended_agents = ["executor"]  # default
        priority = "medium"
        
        for keyword, agents in self.routing_rules.items():
            if keyword in request_lower:
                recommended_agents = agents
                break
        
        # Determine complexity and priority
        if len(request.split()) > 100 or "complex" in request_lower or "urgent" in request_lower:
            priority = "high"
        elif len(request.split()) < 20:
            priority = "low"
            
        return {
            "recommended_agents": recommended_agents,
            "priority": priority,
            "complexity": "high" if priority == "high" else "medium",
            "request_type": self._classify_request_type(request_lower)
        }
    
    def _classify_request_type(self, request: str) -> str:
        """Classify the type of request."""
        if any(word in request for word in ["code", "function", "class", "method"]):
            return "code"
        elif any(word in request for word in ["research", "analyze", "study", "investigate"]):
            return "research"
        elif any(word in request for word in ["strategic", "plan", "roadmap", "vision"]):
            return "strategic"
        elif any(word in request for word in ["test", "unit test", "testing"]):
            return "testing"
        elif any(word in request for word in ["debug", "error", "bug", "fix"]):
            return "debugging"
        else:
            return "general"
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the triage agent."""
        return """You are a triage specialist responsible for:
        - Analyzing incoming requests and determining urgency
        - Routing tasks to the most appropriate specialist
        - Breaking down complex problems into manageable components
        - Providing initial assessment and recommendations
        - Coordinating multi-agent workflows
        
        Provide clear analysis including:
        1. Request classification and complexity assessment
        2. Urgency and priority level
        3. Recommended approach and agent routing
        4. Key considerations and potential challenges
        5. Success criteria and expected outcomes"""
    
    async def _call_openai_async(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenAI API asynchronously."""
        loop = asyncio.get_event_loop()
        
        def _call_sync():
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=800
            )
            return response.choices[0].message.content
        
        return await loop.run_in_executor(None, _call_sync)


class CodeDebuggerAgent(AgentBase):
    """
    Enhanced Code Debugger Agent with MindMeld framework integration.
    Specialized in identifying and debugging code issues.
    """
    
    REQUIRED_CONFIG_FIELDS = ['openai_client', 'model']
    DEFAULT_CAPABILITIES = [
        AgentCapability.CODE_DEBUGGING,
        AgentCapability.CODE_ANALYSIS
    ]
    
    def __init__(self, name: str, agent_type: str, config: Dict[str, Any]):
        super().__init__(name, agent_type, config, self.DEFAULT_CAPABILITIES)
        self.openai_client = config.get('openai_client', client)
        self.model = config.get('model', 'gpt-4')
        
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate code debugger input."""
        required_fields = ['code']
        return all(field in input_data for field in required_fields)
        
    def validate_output(self, output_data: Any) -> bool:
        """Validate code debugger output."""
        return output_data is not None and isinstance(output_data, str)
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Debug code and identify issues."""
        code = input_data.get('code', '')
        if not code:
            raise ValidationError("Code is required for debugging")
            
        error_message = input_data.get('error_message', '')
        language = input_data.get('language', 'python')
        
        if not self.openai_client:
            raise AgentExecutionError("OpenAI client not available")
        
        try:
            messages = [
                {
                    "role": "system", 
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user", 
                    "content": self._format_debug_request(code, error_message, language)
                }
            ]
            
            response = await self._call_openai_async(messages)
            
            return AgentResponse(
                success=True,
                result=response,
                agent_type=self.agent_type,
                timestamp=self._get_timestamp(),
                metadata={
                    "model": self.model,
                    "language": language,
                    "has_error_message": bool(error_message)
                }
            )
            
        except Exception as e:
            raise AgentExecutionError(f"Code debugger execution failed: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the code debugger."""
        return """You are an expert code debugging agent. For any provided code and error:
        1. Identify the root cause of the issue
        2. Explain why the error occurs in detail
        3. Provide step-by-step debugging approach
        4. Suggest multiple solution approaches with trade-offs
        5. Highlight preventive measures for similar issues
        6. Include code examples for fixes when applicable
        
        Format your response as a structured debugging report with clear sections."""
    
    def _format_debug_request(self, code: str, error_message: str, language: str) -> str:
        """Format the debugging request."""
        request = f"Debug this {language} code:\n\n```{language}\n{code}\n```"
        if error_message:
            request += f"\n\nError message:\n```\n{error_message}\n```"
        return request
    
    async def _call_openai_async(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenAI API asynchronously."""
        loop = asyncio.get_event_loop()
        
        def _call_sync():
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=1500
            )
            return response.choices[0].message.content
        
        return await loop.run_in_executor(None, _call_sync)


class CodeRepairAgent(AgentBase):
    """
    Enhanced Code Repair Agent with MindMeld framework integration.
    Specialized in fixing and optimizing code issues.
    """
    
    REQUIRED_CONFIG_FIELDS = ['openai_client', 'model']
    DEFAULT_CAPABILITIES = [
        AgentCapability.CODE_REPAIR,
        AgentCapability.CODE_ANALYSIS
    ]
    
    def __init__(self, name: str, agent_type: str, config: Dict[str, Any]):
        super().__init__(name, agent_type, config, self.DEFAULT_CAPABILITIES)
        self.openai_client = config.get('openai_client', client)
        self.model = config.get('model', 'gpt-4')
        
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate code repair input."""
        required_fields = ['code']
        return all(field in input_data for field in required_fields)
        
    def validate_output(self, output_data: Any) -> bool:
        """Validate code repair output."""
        return output_data is not None and isinstance(output_data, str)
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Repair and fix code issues."""
        code = input_data.get('code', '')
        if not code:
            raise ValidationError("Code is required for repair")
            
        issues = input_data.get('issues', '')
        repair_type = input_data.get('repair_type', 'general')
        language = input_data.get('language', 'python')
        
        if not self.openai_client:
            raise AgentExecutionError("OpenAI client not available")
        
        try:
            messages = [
                {
                    "role": "system", 
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user", 
                    "content": self._format_repair_request(code, issues, repair_type, language)
                }
            ]
            
            response = await self._call_openai_async(messages)
            
            return AgentResponse(
                success=True,
                result=response,
                agent_type=self.agent_type,
                timestamp=self._get_timestamp(),
                metadata={
                    "model": self.model,
                    "language": language,
                    "repair_type": repair_type,
                    "has_issues": bool(issues)
                }
            )
            
        except Exception as e:
            raise AgentExecutionError(f"Code repair execution failed: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the code repair agent."""
        return """You are an expert code repair agent. For any provided code:
        1. Fix all identified issues and bugs thoroughly
        2. Improve code quality, readability, and maintainability
        3. Optimize performance where possible without breaking functionality
        4. Ensure best practices and coding standards are followed
        5. Add necessary comments and documentation
        6. Provide the corrected code with detailed explanations
        
        Return both the fixed code and a comprehensive explanation of changes made."""
    
    def _format_repair_request(self, code: str, issues: str, repair_type: str, language: str) -> str:
        """Format the repair request."""
        request = f"Repair this {language} code ({repair_type} repair):\n\n```{language}\n{code}\n```"
        if issues:
            request += f"\n\nKnown issues to fix:\n{issues}"
        return request
    
    async def _call_openai_async(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenAI API asynchronously."""
        loop = asyncio.get_event_loop()
        
        def _call_sync():
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        
        return await loop.run_in_executor(None, _call_sync)


class PerformanceProfilerAgent(AgentBase):
    """
    Enhanced Performance Profiler Agent with MindMeld framework integration.
    Specialized in analyzing and optimizing code performance.
    """
    
    REQUIRED_CONFIG_FIELDS = ['openai_client', 'model']
    DEFAULT_CAPABILITIES = [
        AgentCapability.PERFORMANCE_ANALYSIS,
        AgentCapability.CODE_ANALYSIS
    ]
    
    def __init__(self, name: str, agent_type: str, config: Dict[str, Any]):
        super().__init__(name, agent_type, config, self.DEFAULT_CAPABILITIES)
        self.openai_client = config.get('openai_client', client)
        self.model = config.get('model', 'gpt-4')
        
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate performance profiler input."""
        required_fields = ['code']
        return all(field in input_data for field in required_fields)
        
    def validate_output(self, output_data: Any) -> bool:
        """Validate performance profiler output."""
        return output_data is not None and isinstance(output_data, str)
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Analyze and optimize code performance."""
        code = input_data.get('code', '')
        if not code:
            raise ValidationError("Code is required for performance analysis")
            
        language = input_data.get('language', 'python')
        focus_area = input_data.get('focus_area', 'general')
        optimization_level = input_data.get('optimization_level', 'moderate')
        
        if not self.openai_client:
            raise AgentExecutionError("OpenAI client not available")
        
        try:
            messages = [
                {
                    "role": "system", 
                    "content": self._get_system_prompt(optimization_level)
                },
                {
                    "role": "user", 
                    "content": self._format_profiling_request(code, language, focus_area)
                }
            ]
            
            response = await self._call_openai_async(messages)
            
            return AgentResponse(
                success=True,
                result=response,
                agent_type=self.agent_type,
                timestamp=self._get_timestamp(),
                metadata={
                    "model": self.model,
                    "language": language,
                    "focus_area": focus_area,
                    "optimization_level": optimization_level
                }
            )
            
        except Exception as e:
            raise AgentExecutionError(f"Performance profiler execution failed: {str(e)}")
    
    def _get_system_prompt(self, optimization_level: str) -> str:
        """Get the system prompt for the performance profiler."""
        base_prompt = """You are an expert performance profiler. Analyze the code for:
        1. Time complexity analysis (Big O notation)
        2. Space complexity analysis
        3. Performance bottlenecks identification
        4. Memory usage optimization opportunities
        5. Algorithm efficiency improvements
        6. Platform-specific optimizations
        7. Caching opportunities and strategies
        8. Parallelization and concurrency possibilities
        9. Database query optimization (if applicable)
        10. I/O operation optimization
        
        Provide specific, actionable optimization recommendations with code examples."""
        
        if optimization_level == "aggressive":
            base_prompt += "\n\nFocus on maximum performance gains, even if they require significant code changes."
        elif optimization_level == "conservative":
            base_prompt += "\n\nFocus on safe optimizations that don't significantly change code structure."
            
        return base_prompt
    
    def _format_profiling_request(self, code: str, language: str, focus_area: str) -> str:
        """Format the profiling request."""
        return f"Profile this {language} code (focus: {focus_area}):\n\n```{language}\n{code}\n```"
    
    async def _call_openai_async(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenAI API asynchronously."""
        loop = asyncio.get_event_loop()
        
        def _call_sync():
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=2000
            )
            return response.choices[0].message.content
        
        return await loop.run_in_executor(None, _call_sync)


class TestGeneratorAgent(AgentBase):
    """
    Enhanced Test Generator Agent with MindMeld framework integration.
    Specialized in generating comprehensive test suites.
    """
    
    REQUIRED_CONFIG_FIELDS = ['openai_client', 'model']
    DEFAULT_CAPABILITIES = [
        AgentCapability.TEST_GENERATION,
        AgentCapability.CODE_ANALYSIS
    ]
    
    def __init__(self, name: str, agent_type: str, config: Dict[str, Any]):
        super().__init__(name, agent_type, config, self.DEFAULT_CAPABILITIES)
        self.openai_client = config.get('openai_client', client)
        self.model = config.get('model', 'gpt-4')
        
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate test generator input."""
        required_fields = ['code']
        return all(field in input_data for field in required_fields)
        
    def validate_output(self, output_data: Any) -> bool:
        """Validate test generator output."""
        return output_data is not None and isinstance(output_data, str)
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Generate comprehensive test suites for code."""
        code = input_data.get('code', '')
        if not code:
            raise ValidationError("Code is required for test generation")
            
        language = input_data.get('language', 'python')
        test_framework = input_data.get('test_framework', 'pytest')
        test_types = input_data.get('test_types', ['unit', 'integration'])
        coverage_level = input_data.get('coverage_level', 'comprehensive')
        
        if not self.openai_client:
            raise AgentExecutionError("OpenAI client not available")
        
        try:
            messages = [
                {
                    "role": "system", 
                    "content": self._get_system_prompt(test_framework, coverage_level)
                },
                {
                    "role": "user", 
                    "content": self._format_test_request(code, language, test_types)
                }
            ]
            
            response = await self._call_openai_async(messages)
            
            return AgentResponse(
                success=True,
                result=response,
                agent_type=self.agent_type,
                timestamp=self._get_timestamp(),
                metadata={
                    "model": self.model,
                    "language": language,
                    "test_framework": test_framework,
                    "test_types": test_types,
                    "coverage_level": coverage_level
                }
            )
            
        except Exception as e:
            raise AgentExecutionError(f"Test generator execution failed: {str(e)}")
    
    def _get_system_prompt(self, test_framework: str, coverage_level: str) -> str:
        """Get the system prompt for the test generator."""
        prompt = f"""You are an expert test generation agent using {test_framework}. Generate comprehensive tests including:
        1. Unit tests for individual functions/methods
        2. Integration tests for component interactions
        3. Edge case testing and boundary conditions
        4. Error handling and exception testing
        5. Performance and load testing scenarios
        6. Mocking and stubbing for external dependencies
        7. Data validation and input sanitization tests
        8. Regression testing scenarios
        
        Follow {test_framework} best practices and conventions."""
        
        if coverage_level == "comprehensive":
            prompt += "\n\nAim for maximum test coverage including all code paths and scenarios."
        elif coverage_level == "focused":
            prompt += "\n\nFocus on critical functionality and high-risk areas."
            
        return prompt
    
    def _format_test_request(self, code: str, language: str, test_types: List[str]) -> str:
        """Format the test generation request."""
        types_str = ", ".join(test_types)
        return f"Generate {types_str} tests for this {language} code:\n\n```{language}\n{code}\n```"
    
    async def _call_openai_async(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenAI API asynchronously."""
        loop = asyncio.get_event_loop()
        
        def _call_sync():
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=2500
            )
            return response.choices[0].message.content
        
        return await loop.run_in_executor(None, _call_sync)


class ImageAgent(AgentBase):
    """
    Enhanced Image Agent with MindMeld framework integration.
    Specialized in image processing and visual analysis.
    """
    
    REQUIRED_CONFIG_FIELDS = ['openai_client', 'model']
    DEFAULT_CAPABILITIES = [
        AgentCapability.IMAGE_PROCESSING,
        AgentCapability.VISUAL_ANALYSIS
    ]
    
    def __init__(self, name: str, agent_type: str, config: Dict[str, Any]):
        super().__init__(name, agent_type, config, self.DEFAULT_CAPABILITIES)
        self.openai_client = config.get('openai_client', client)
        self.model = config.get('model', 'gpt-4-vision-preview')
        
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate image agent input."""
        # For image processing, we need either an image URL, path, or processing query
        return any(field in input_data for field in ['image_url', 'image_path', 'query'])
        
    def validate_output(self, output_data: Any) -> bool:
        """Validate image agent output."""
        return output_data is not None and isinstance(output_data, str)
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Process and analyze images."""
        query = input_data.get('query', 'Analyze this image')
        image_url = input_data.get('image_url')
        image_path = input_data.get('image_path')
        analysis_type = input_data.get('analysis_type', 'general')
        detail_level = input_data.get('detail_level', 'high')
        
        if not self.openai_client:
            raise AgentExecutionError("OpenAI client not available")
        
        try:
            if image_url or image_path:
                # If we have an actual image, we'd use vision capabilities
                # For now, we'll provide guidance on image processing
                response = await self._process_image_query(query, analysis_type, detail_level)
            else:
                # Handle general image processing queries
                response = await self._handle_image_query(query, analysis_type)
            
            return AgentResponse(
                success=True,
                result=response,
                agent_type=self.agent_type,
                timestamp=self._get_timestamp(),
                metadata={
                    "model": self.model,
                    "analysis_type": analysis_type,
                    "detail_level": detail_level,
                    "has_image": bool(image_url or image_path)
                }
            )
            
        except Exception as e:
            raise AgentExecutionError(f"Image agent execution failed: {str(e)}")
    
    async def _process_image_query(self, query: str, analysis_type: str, detail_level: str) -> str:
        """Process image-related queries with vision capabilities."""
        messages = [
            {
                "role": "system", 
                "content": self._get_system_prompt(analysis_type)
            },
            {
                "role": "user", 
                "content": f"Image processing request: {query}\nAnalysis type: {analysis_type}\nDetail level: {detail_level}"
            }
        ]
        
        return await self._call_openai_async(messages)
    
    async def _handle_image_query(self, query: str, analysis_type: str) -> str:
        """Handle general image processing queries."""
        messages = [
            {
                "role": "system", 
                "content": self._get_system_prompt(analysis_type)
            },
            {
                "role": "user", 
                "content": query
            }
        ]
        
        return await self._call_openai_async(messages)
    
    def _get_system_prompt(self, analysis_type: str) -> str:
        """Get the system prompt for the image agent."""
        base_prompt = """You are an expert image processing and computer vision specialist. You help with:
        - Image analysis and interpretation
        - Computer vision techniques and algorithms
        - Image processing workflows and pipelines
        - Visual content optimization
        - Object detection and recognition guidance
        - Image enhancement and filtering techniques
        - Format conversion and compression strategies
        - Machine learning for visual tasks
        
        Provide practical solutions, code examples, and technical guidance."""
        
        if analysis_type == "technical":
            base_prompt += "\n\nFocus on technical implementation details and computer vision algorithms."
        elif analysis_type == "creative":
            base_prompt += "\n\nFocus on creative applications and artistic image processing techniques."
        elif analysis_type == "optimization":
            base_prompt += "\n\nFocus on performance optimization and efficient image processing."
            
        return base_prompt
    
    async def _call_openai_async(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenAI API asynchronously."""
        loop = asyncio.get_event_loop()
        
        def _call_sync():
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.6,
                max_tokens=1500
            )
            return response.choices[0].message.content
        
        return await loop.run_in_executor(None, _call_sync)


class AudioAgent(AgentBase):
    """
    Enhanced Audio Agent with MindMeld framework integration.
    Specialized in audio processing and speech analysis.
    """
    
    REQUIRED_CONFIG_FIELDS = ['openai_client', 'model']
    DEFAULT_CAPABILITIES = [
        AgentCapability.AUDIO_PROCESSING,
        AgentCapability.SPEECH_ANALYSIS
    ]
    
    def __init__(self, name: str, agent_type: str, config: Dict[str, Any]):
        super().__init__(name, agent_type, config, self.DEFAULT_CAPABILITIES)
        self.openai_client = config.get('openai_client', client)
        self.model = config.get('model', 'gpt-4')
        self.whisper_model = config.get('whisper_model', 'whisper-1')
        
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate audio agent input."""
        # For audio processing, we need either an audio file, URL, or processing query
        return any(field in input_data for field in ['audio_url', 'audio_path', 'query'])
        
    def validate_output(self, output_data: Any) -> bool:
        """Validate audio agent output."""
        return output_data is not None and isinstance(output_data, str)
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Process and analyze audio."""
        query = input_data.get('query', 'Process this audio')
        audio_url = input_data.get('audio_url')
        audio_path = input_data.get('audio_path')
        task_type = input_data.get('task_type', 'analysis')
        language = input_data.get('language', 'en')
        
        if not self.openai_client:
            raise AgentExecutionError("OpenAI client not available")
        
        try:
            if audio_url or audio_path:
                # If we have an actual audio file, we'd use transcription capabilities
                response = await self._process_audio_file(query, task_type, language)
            else:
                # Handle general audio processing queries
                response = await self._handle_audio_query(query, task_type)
            
            return AgentResponse(
                success=True,
                result=response,
                agent_type=self.agent_type,
                timestamp=self._get_timestamp(),
                metadata={
                    "model": self.model,
                    "task_type": task_type,
                    "language": language,
                    "has_audio": bool(audio_url or audio_path)
                }
            )
            
        except Exception as e:
            raise AgentExecutionError(f"Audio agent execution failed: {str(e)}")
    
    async def _process_audio_file(self, query: str, task_type: str, language: str) -> str:
        """Process audio file-related queries."""
        messages = [
            {
                "role": "system", 
                "content": self._get_system_prompt(task_type)
            },
            {
                "role": "user", 
                "content": f"Audio processing request: {query}\nTask type: {task_type}\nLanguage: {language}"
            }
        ]
        
        return await self._call_openai_async(messages)
    
    async def _handle_audio_query(self, query: str, task_type: str) -> str:
        """Handle general audio processing queries."""
        messages = [
            {
                "role": "system", 
                "content": self._get_system_prompt(task_type)
            },
            {
                "role": "user", 
                "content": query
            }
        ]
        
        return await self._call_openai_async(messages)
    
    def _get_system_prompt(self, task_type: str) -> str:
        """Get the system prompt for the audio agent."""
        base_prompt = """You are an expert audio processing and speech analysis specialist. You help with:
        - Audio transcription and speech-to-text
        - Audio analysis and manipulation
        - Audio format conversion and optimization
        - Sound quality improvement and noise reduction
        - Music and speech analysis
        - Audio feature extraction
        - Real-time audio processing
        - Voice recognition and speaker identification
        
        Provide practical solutions, code examples, and technical guidance."""
        
        if task_type == "transcription":
            base_prompt += "\n\nFocus on speech-to-text accuracy and transcription best practices."
        elif task_type == "analysis":
            base_prompt += "\n\nFocus on audio analysis techniques and signal processing."
        elif task_type == "enhancement":
            base_prompt += "\n\nFocus on audio quality improvement and noise reduction."
            
        return base_prompt
    
    async def _call_openai_async(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenAI API asynchronously."""
        loop = asyncio.get_event_loop()
        
        def _call_sync():
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1500
            )
            return response.choices[0].message.content
        
        return await loop.run_in_executor(None, _call_sync)


# Export enhanced agents
__all__ = [
    'CEOAgent',
    'ResearchAgent', 
    'CodeAnalysisAgent',
    'TriageAgent',
    'CodeDebuggerAgent',
    'CodeRepairAgent',
    'PerformanceProfilerAgent',
    'TestGeneratorAgent',
    'ImageAgent',
    'AudioAgent'
]
