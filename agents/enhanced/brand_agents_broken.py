"""
Enhanced Brand Deconstruction Agents
Specialized agents for brand analysis, satirical content creation, and image generation
using the pentagram framework and direct gpt-image-1 integration.
"""

import asyncio
import os
import time
import json
import base64
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from datetime import datetime

# Import from the existing shared framework
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_agents'))

from shared_agents.core.agent_factory import (
    AgentBase, 
    AgentResponse, 
    AgentCapability, 
    AgentExecutionError,
    ValidationError
)

# Import brand-specific capabilities
from shared_agents.core.brand_capabilities import BrandCapability

# Import OpenAI client
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

logger = logging.getLogger(__name__)

@dataclass
class BrandAnalysisRequest:
    """Request structure for brand analysis"""
    brand_name: str
    website_url: Optional[str] = None
    additional_context: Optional[Dict[str, Any]] = None
    analysis_depth: str = "comprehensive"  # "quick", "standard", "comprehensive"
    include_satirical: bool = True

@dataclass
class GPTImageRequest:
    """Request structure for GPT image generation with pentagram framework"""
    prompt: str
    brand_context: Dict[str, Any]
    resolution: str = "1536x1024"  # Maximum quality for gpt-image-1
    quality: str = "hd"
    style: str = "vivid"
    satirical_intensity: float = 0.7
    pentagram_elements: Optional[Dict[str, Any]] = None

@dataclass
class BrandIntelligenceReport:
    """Comprehensive brand intelligence report"""
    brand_name: str
    authenticity_score: float
    positioning_analysis: Dict[str, Any]
    claims_validation: Dict[str, Any]
    satirical_vulnerabilities: List[Dict[str, Any]]
    competitive_landscape: Dict[str, Any]
    visual_assets: List[Dict[str, Any]]
    recommendations: List[str]
    confidence_score: float
    processing_metadata: Dict[str, Any]


class BrandDeconstructionAgent(AgentBase):
    """
    Primary agent for comprehensive brand deconstruction and analysis.
    Integrates positioning analysis, claims validation, and authenticity scoring.
    """
    
    REQUIRED_CONFIG_FIELDS = ['openai_client']
    DEFAULT_CAPABILITIES = [
        AgentCapability.RESEARCH,
        AgentCapability.DATA_PROCESSING,
        AgentCapability.TEXT_GENERATION,
        AgentCapability.STRATEGIC_PLANNING
    ]
    
    def __init__(self, name: str, agent_type: str, config: Dict[str, Any]):
        super().__init__(name, agent_type, config, self.DEFAULT_CAPABILITIES)
        self.openai_client = config.get('openai_client', client)
        self.model = config.get('model', 'gpt-4-turbo')
        
        # Known brand database for fallback analysis
        self.known_brands = {
            "salesforce.com": {
                "name": "Salesforce",
                "positioning": "The Customer Company",
                "key_claims": ["AI-powered CRM", "Customer success", "Trailblazer community"],
                "vulnerabilities": ["AI washing", "Complexity masking", "Scale vs personal"]
            },
            "apple.com": {
                "name": "Apple", 
                "positioning": "Think Different",
                "key_claims": ["Innovation", "Privacy", "Premium design"],
                "vulnerabilities": ["Premium accessibility", "Innovation vs iteration", "Privacy vs data collection"]
            },
            "google.com": {
                "name": "Google",
                "positioning": "Don't be evil / Do the right thing", 
                "key_claims": ["Information accessibility", "Innovation", "Free services"],
                "vulnerabilities": ["Data privacy", "Market dominance", "Free vs surveillance"]
            },
            "microsoft.com": {
                "name": "Microsoft",
                "positioning": "Empower every person",
                "key_claims": ["Productivity", "Cloud-first", "AI for everyone"],
                "vulnerabilities": ["Complexity", "Vendor lock-in", "AI hype"]
            }
        }
    
    async def execute(self, request: Dict[str, Any]) -> AgentResponse:
        """Execute comprehensive brand deconstruction analysis"""
        try:
            start_time = time.time()
            
            # Validate request
            if not isinstance(request, dict):
                request = {"brand_name": str(request)}
            
            brand_request = BrandAnalysisRequest(**request)
            
            # Perform multi-stage analysis
            positioning_analysis = await self._analyze_brand_positioning(brand_request)
            claims_validation = await self._validate_brand_claims(brand_request)
            authenticity_score = await self._calculate_authenticity_score(positioning_analysis, claims_validation)
            competitive_analysis = await self._analyze_competitive_landscape(brand_request)
            satirical_vulnerabilities = await self._identify_satirical_vulnerabilities(brand_request, positioning_analysis)
            
            # Compile comprehensive report
            report = BrandIntelligenceReport(
                brand_name=brand_request.brand_name,
                authenticity_score=authenticity_score,
                positioning_analysis=positioning_analysis,
                claims_validation=claims_validation,
                satirical_vulnerabilities=satirical_vulnerabilities,
                competitive_landscape=competitive_analysis,
                visual_assets=[],  # Will be populated by image agent
                recommendations=await self._generate_recommendations(positioning_analysis, claims_validation),
                confidence_score=self._calculate_confidence_score(positioning_analysis, claims_validation),
                processing_metadata={
                    "processing_time": time.time() - start_time,
                    "agent_name": self.name,
                    "analysis_depth": brand_request.analysis_depth,
                    "model_used": self.model
                }
            )
            
            return AgentResponse(
                success=True,
                result=asdict(report),
                agent_type=self.agent_type,
                timestamp=datetime.now().isoformat(),
                execution_time=time.time() - start_time,
                metadata={
                    "processing_time": time.time() - start_time,
                    "capabilities_used": [cap.value for cap in self.capabilities]
                }
            )
            
        except Exception as e:
            logger.error(f"Brand deconstruction failed: {str(e)}")
            raise AgentExecutionError(f"Brand analysis failed: {str(e)}")
    
    async def _analyze_brand_positioning(self, request: BrandAnalysisRequest) -> Dict[str, Any]:
        """Analyze brand positioning and messaging"""
        try:
            # Check known brands first
            domain = self._extract_domain(request.website_url) if request.website_url else None
            if domain and domain in self.known_brands:
                brand_data = self.known_brands[domain]
                return {
                    "source": "known_database",
                    "positioning": brand_data["positioning"],
                    "key_messages": brand_data["key_claims"],
                    "analysis_method": "database_lookup"
                }
            
            # Use GPT-4 for dynamic analysis
            prompt = f"""
            Analyze the brand positioning for {request.brand_name}.
            
            Provide a comprehensive analysis including:
            1. Core positioning statement
            2. Key value propositions
            3. Target audience
            4. Brand personality traits
            5. Market differentiation strategy
            
            Format as JSON with clear categories.
            """
            
            response = await self._openai_request(prompt)
            return {
                "source": "ai_analysis",
                "analysis": response,
                "analysis_method": "gpt4_analysis"
            }
            
        except Exception as e:
            logger.error(f"Positioning analysis failed: {str(e)}")
            return {"error": str(e), "source": "error"}
    
    async def _validate_brand_claims(self, request: BrandAnalysisRequest) -> Dict[str, Any]:
        """Validate brand claims against market reality"""
        try:
            domain = self._extract_domain(request.website_url) if request.website_url else None
            if domain and domain in self.known_brands:
                brand_data = self.known_brands[domain]
                return {
                    "claims": brand_data["key_claims"],
                    "validation_status": "database_reference",
                    "credibility_gaps": brand_data.get("vulnerabilities", [])
                }
            
            prompt = f"""
            Validate the key claims made by {request.brand_name}.
            
            For each major claim:
            1. Evidence supporting the claim
            2. Contradictory evidence or market reality
            3. Credibility assessment (1-10)
            4. Potential vulnerabilities for satirical content
            
            Focus on gaps between claimed positioning and actual performance.
            """
            
            response = await self._openai_request(prompt)
            return {
                "validation_analysis": response,
                "validation_method": "comprehensive_analysis"
            }
            
        except Exception as e:
            logger.error(f"Claims validation failed: {str(e)}")
            return {"error": str(e)}
    
    async def _calculate_authenticity_score(self, positioning: Dict[str, Any], claims: Dict[str, Any]) -> float:
        """Calculate overall brand authenticity score"""
        try:
            # Simple scoring algorithm - can be enhanced
            base_score = 0.5
            
            # Boost for consistent messaging
            if positioning.get("source") == "known_database" and claims.get("validation_status") == "database_reference":
                base_score += 0.2
            
            # Reduce for known vulnerabilities
            vulnerabilities = claims.get("credibility_gaps", [])
            if vulnerabilities:
                base_score -= len(vulnerabilities) * 0.1
            
            return max(0.0, min(1.0, base_score))
            
        except Exception:
            return 0.5  # Neutral score on error
    
    async def _analyze_competitive_landscape(self, request: BrandAnalysisRequest) -> Dict[str, Any]:
        """Analyze competitive positioning"""
        try:
            prompt = f"""
            Analyze the competitive landscape for {request.brand_name}.
            
            Include:
            1. Main competitors
            2. Competitive advantages claimed
            3. Market positioning gaps
            4. Opportunities for differentiation
            5. Satirical angles based on competitive dynamics
            """
            
            response = await self._openai_request(prompt)
            return {"competitive_analysis": response}
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _identify_satirical_vulnerabilities(self, request: BrandAnalysisRequest, positioning: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential satirical angles"""
        try:
            vulnerabilities = []
            
            # Known vulnerabilities
            domain = self._extract_domain(request.website_url) if request.website_url else None
            if domain and domain in self.known_brands:
                known_vulns = self.known_brands[domain].get("vulnerabilities", [])
                for vuln in known_vulns:
                    vulnerabilities.append({
                        "vulnerability": vuln,
                        "satirical_potential": 0.8,
                        "source": "known_database"
                    })
            
            # AI-generated vulnerabilities
            prompt = f"""
            Identify satirical vulnerabilities for {request.brand_name}.
            
            Focus on:
            1. Gaps between claims and reality
            2. Industry-wide hypocrisy
            3. Corporate doublespeak
            4. Absurd market positioning
            
            Return specific, actionable satirical angles.
            """
            
            ai_response = await self._openai_request(prompt)
            vulnerabilities.append({
                "ai_generated_vulnerabilities": ai_response,
                "satirical_potential": 0.7,
                "source": "ai_analysis"
            })
            
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"Satirical vulnerability analysis failed: {str(e)}")
            return [{"error": str(e)}]
    
    async def _generate_recommendations(self, positioning: Dict[str, Any], claims: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if positioning.get("error") or claims.get("error"):
            recommendations.append("Conduct deeper brand analysis with additional data sources")
        
        if claims.get("credibility_gaps"):
            recommendations.append("Address credibility gaps in brand messaging")
        
        recommendations.extend([
            "Develop satirical content targeting identified vulnerabilities",
            "Monitor competitive positioning shifts",
            "Create visual content highlighting brand contradictions"
        ])
        
        return recommendations
    
    def _calculate_confidence_score(self, positioning: Dict[str, Any], claims: Dict[str, Any]) -> float:
        """Calculate confidence in analysis quality"""
        score = 0.5
        
        if positioning.get("source") == "known_database":
            score += 0.3
        if claims.get("validation_status") == "database_reference":
            score += 0.2
        
        return min(1.0, score)
    
    def _extract_domain(self, url: Optional[str]) -> Optional[str]:
        """Extract domain from URL"""
        if not url:
            return None
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.lower().replace('www.', '')
        except:
            return None
    
    async def _openai_request(self, prompt: str) -> str:
        """Make OpenAI API request"""
        if not self.openai_client:
            raise AgentExecutionError("OpenAI client not configured")
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise AgentExecutionError(f"OpenAI request failed: {str(e)}")


class GPTImageGenerationAgent(AgentBase):
    """
    Specialized agent for gpt-image-1 integration with pentagram framework.
    Generates high-quality satirical brand imagery.
    """
    
    REQUIRED_CONFIG_FIELDS = ['openai_client']
    DEFAULT_CAPABILITIES = [
        AgentCapability.IMAGE_PROCESSING,
        AgentCapability.VISUAL_ANALYSIS,
        AgentCapability.TEXT_GENERATION
    ]
    
    def __init__(self, name: str, agent_type: str, config: Dict[str, Any]):
        super().__init__(name, agent_type, config, self.DEFAULT_CAPABILITIES)
        self.openai_client = config.get('openai_client', client)
        self.max_resolution = "1536x1024"  # Maximum for gpt-image-1
        self.quality = "hd"
        
    async def execute(self, request: Dict[str, Any]) -> AgentResponse:
        """Execute image generation with pentagram framework"""
        try:
            start_time = time.time()
            
            # Validate and parse request
            image_request = GPTImageRequest(**request)
            
            # Apply pentagram framework
            pentagram_prompt = await self._create_pentagram_prompt(image_request)
            
            # Generate image with maximum quality
            image_result = await self._generate_image(pentagram_prompt, image_request)
            
            # Process and validate result
            if image_result.success:
                return AgentResponse(
                    success=True,
                    result={
                        "image_url": image_result.image_url,
                        "image_data": image_result.image_data,
                        "pentagram_elements": image_request.pentagram_elements,
                        "generation_metadata": image_result.generation_metadata,
                        "prompt_used": pentagram_prompt
                    },
                    agent_type=self.agent_type,
                    timestamp=datetime.now().isoformat(),
                    execution_time=time.time() - start_time,
                    metadata={
                        "processing_time": time.time() - start_time,
                        "resolution": image_request.resolution,
                        "quality": image_request.quality
                    }
                )
            else:
                raise AgentExecutionError(f"Image generation failed: {image_result.error_message}")
                
        except Exception as e:
            logger.error(f"GPT image generation failed: {str(e)}")
            raise AgentExecutionError(f"Image generation failed: {str(e)}")
    
    async def _create_pentagram_prompt(self, request: GPTImageRequest) -> str:
        """Create prompt using pentagram framework for maximum satirical impact"""
        
        # Default pentagram elements if not provided
        pentagram_elements = request.pentagram_elements or {
            "intent_clarity": "Expose brand contradictions through visual satire",
            "fidelity_pass": "Maintain recognizable brand elements while subverting meaning",
            "symbolic_anchoring": "Corporate imagery with absurdist elements",
            "environmental_context": "Professional setting with satirical disruption",
            "brand_world_constraints": "Stay within legal parody boundaries"
        }
        
        # Update request with pentagram elements
        request.pentagram_elements = pentagram_elements
        
        # Construct comprehensive prompt
        base_prompt = request.prompt
        brand_context = request.brand_context
        
        pentagram_prompt = f"""
        {base_prompt}
        
        PENTAGRAM FRAMEWORK APPLICATION:
        Intent Clarity: {pentagram_elements['intent_clarity']}
        Fidelity Pass: {pentagram_elements['fidelity_pass']}
        Symbolic Anchoring: {pentagram_elements['symbolic_anchoring']}
        Environmental Context: {pentagram_elements['environmental_context']}
        Brand World Constraints: {pentagram_elements['brand_world_constraints']}
        
        BRAND CONTEXT:
        Brand Name: {brand_context.get('brand_name', 'Unknown Brand')}
        Industry: {brand_context.get('industry', 'Technology')}
        Key Claims: {brand_context.get('key_claims', [])}
        Vulnerabilities: {brand_context.get('vulnerabilities', [])}
        
        SATIRICAL INTENSITY: {request.satirical_intensity}/1.0
        
        Create a visually striking, professionally executed satirical image that exposes brand contradictions while maintaining artistic quality and legal compliance.
        """
        
        return pentagram_prompt
    
    async def _generate_image(self, prompt: str, request: GPTImageRequest) -> 'GPTImage1Result':
        """Generate image using gpt-image-1 with maximum quality settings"""
        try:
            if not self.openai_client:
                raise AgentExecutionError("OpenAI client not configured")
            
            # Prepare generation parameters
            generation_params = {
                "model": "gpt-image-1",  # Explicitly use gpt-image-1
                "prompt": prompt,
                "size": "1536x1024",  # Use maximum resolution for gpt-image-1
                "quality": request.quality,
                "style": request.style,
                "n": 1
            }
            
            # Generate image
            start_time = time.time()
            response = self.openai_client.images.generate(**generation_params)
            processing_time = time.time() - start_time
            
            # Extract result
            image_url = response.data[0].url if response.data else None
            
            return GPTImage1Result(
                success=True,
                image_url=image_url,
                generation_metadata={
                    "model": "gpt-image-1",
                    "resolution": request.resolution,
                    "quality": request.quality,
                    "style": request.style,
                    "prompt_length": len(prompt)
                },
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return GPTImage1Result(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time if 'start_time' in locals() else 0.0
            )


class BrandIntelligenceAgent(AgentBase):
    """
    Market intelligence and brand insights agent.
    Provides market trends, consumer insights, and strategic intelligence.
    """
    
    def __init__(self, name: str = "BrandIntelligenceAgent", **config):
        super().__init__(name, **config)
        self.capabilities = [
            AgentCapability.RESEARCH,
            AgentCapability.ANALYSIS,
            AgentCapability.DATA_PROCESSING,
            BrandCapability.MARKET_INTELLIGENCE
        ]
    
    async def execute(self, query: str, intelligence_type: str = "market_trends") -> AgentResponse:
        """
        Generate brand intelligence insights.
        
        Args:
            query: Research query or brand/market to analyze
            intelligence_type: Type of intelligence (market_trends, consumer_insights, 
                              competitive_intel, opportunity_analysis)
        
        Returns:
            Intelligence report with insights and recommendations
        """
        try:
            if intelligence_type == "market_trends":
                return await self._market_trends_analysis(query)
            elif intelligence_type == "consumer_insights":
                return await self._consumer_insights_analysis(query)
            elif intelligence_type == "competitive_intel":
                return await self._competitive_intelligence(query)
            elif intelligence_type == "opportunity_analysis":
                return await self._opportunity_analysis(query)
            else:
                return await self._comprehensive_intelligence(query)
                
        except Exception as e:
            logger.error(f"Brand intelligence failed: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                result="Failed to generate intelligence"
            )
    
    async def _market_trends_analysis(self, query: str) -> AgentResponse:
        """Analyze market trends and opportunities."""
        prompt = f"""
        As a market intelligence analyst, provide comprehensive market trends analysis for: {query}

        Include:

        1. CURRENT MARKET TRENDS:
           - Emerging trends affecting this market
           - Consumer behavior shifts
           - Technology impacts
           - Regulatory changes
           - Economic factors

        2. FUTURE PROJECTIONS:
           - 6-month outlook
           - 1-year projections
           - 3-year strategic view
           - Key milestones to watch

        3. OPPORTUNITY IDENTIFICATION:
           - Market gaps and white spaces
           - Underserved segments
           - Innovation opportunities
           - Partnership possibilities

        4. RISK ASSESSMENT:
           - Market threats
           - Competitive risks
           - External disruptions
           - Mitigation strategies

        5. STRATEGIC IMPLICATIONS:
           - Strategic recommendations
           - Investment priorities
           - Timeline considerations
           - Success metrics

        Provide data-driven insights with confidence levels and supporting evidence.
        Format as structured JSON for easy parsing.
        """
        
        response = await self._safe_execute({"prompt": prompt})
        
        return AgentResponse(
            success=response.success,
            result={
                "intelligence_type": "market_trends",
                "market_intelligence": response.result if response.success else "Analysis failed",
                "confidence_level": "high",
                "timestamp": datetime.now().isoformat()
            },
            agent_type=self.agent_type,
            timestamp=datetime.now().isoformat()
        )
        """Analyze consumer insights and behavior patterns."""
        prompt = f"""
        Generate consumer insights analysis for: {query}
        
        Include:
        1. Consumer behavior patterns
        2. Demographic insights
        3. Psychographic profiles
        4. Purchase drivers
        5. Brand perception analysis
        """
        
        response = await self._safe_execute({"prompt": prompt})
        
        return AgentResponse(
            success=response.success,
            result={
                "intelligence_type": "consumer_insights",
                "consumer_intelligence": response.result if response.success else "Analysis failed",
                "confidence_level": "medium",
                "timestamp": datetime.now().isoformat()
            },
            agent_type=self.agent_type
        )
    
    async def _competitive_intelligence(self, query: str) -> AgentResponse:
        """Generate competitive intelligence analysis."""
        prompt = f"""
        Provide competitive intelligence analysis for: {query}
        
        Include:
        1. Competitor landscape
        2. Market positioning
        3. Competitive advantages
        4. Threats and opportunities
        5. Strategic recommendations
        """
        
        response = await self._safe_execute({"prompt": prompt})
        
        return AgentResponse(
            success=response.success,
            result={
                "intelligence_type": "competitive_intel",
                "competitive_intelligence": response.result if response.success else "Analysis failed",
                "confidence_level": "high",
                "timestamp": datetime.now().isoformat()
            },
            agent_type=self.agent_type
        )
    
    async def _opportunity_analysis(self, query: str) -> AgentResponse:
        """Analyze market opportunities and potential."""
        prompt = f"""
        Conduct opportunity analysis for: {query}
        
        Include:
        1. Market opportunities
        2. Growth potential
        3. Investment areas
        4. Risk assessment
        5. Strategic priorities
        """
        
        response = await self._safe_execute({"prompt": prompt})
        
        return AgentResponse(
            success=response.success,
            result={
                "intelligence_type": "opportunity_analysis",
                "opportunity_intelligence": response.result if response.success else "Analysis failed",
                "confidence_level": "medium",
                "timestamp": datetime.now().isoformat()
            },
            agent_type=self.agent_type
        )
    
    async def _comprehensive_intelligence(self, query: str) -> AgentResponse:
        """Generate comprehensive brand intelligence."""
        prompt = f"""
        Provide comprehensive brand intelligence for: {query}
        
        Include all aspects:
        1. Market trends
        2. Consumer insights  
        3. Competitive landscape
        4. Opportunities and threats
        5. Strategic recommendations
        """
        
        response = await self._safe_execute({"prompt": prompt})
        
        return AgentResponse(
            success=response.success,
            result={
                "intelligence_type": "comprehensive",
                "comprehensive_intelligence": response.result if response.success else "Analysis failed",
                "confidence_level": "high",
                "timestamp": datetime.now().isoformat()
            },
            agent_type=self.agent_type
        )
        """Analyze market trends and opportunities."""
        prompt = f"""
        As a market intelligence analyst, provide comprehensive market trends analysis for: {query}

        Include:

        1. CURRENT MARKET TRENDS:
           - Emerging trends affecting this market
           - Consumer behavior shifts
           - Technology impacts
           - Regulatory changes
           - Economic factors

        2. FUTURE PROJECTIONS:
           - 6-month outlook
           - 1-year projections
           - 3-year strategic view
           - Key milestones to watch

        3. OPPORTUNITY IDENTIFICATION:
           - Market gaps and white spaces
           - Underserved segments
           - Innovation opportunities
           - Partnership possibilities

        4. RISK ASSESSMENT:
           - Market threats
           - Competitive risks
           - External disruptions
           - Mitigation strategies

        5. STRATEGIC IMPLICATIONS:
           - Strategic recommendations
           - Investment priorities
           - Timeline considerations
           - Success metrics

        Provide data-driven insights with confidence levels and supporting evidence.
        Format as structured JSON for easy parsing.
        """
        
        response = await self._safe_execute(prompt)
        
        return AgentResponse(
            success=response.success,
            result={
                "intelligence_type": "market_trends",
                "market_intelligence": response.result if response.success else "Analysis failed",
                "confidence_level": "high",
                "timestamp": datetime.now().isoformat()
            }
        )


class ElevenLabsTTSAgent(AgentBase):
    """
    Advanced Text-to-Speech agent using ElevenLabs API.
    Provides high-quality voice synthesis with multiple voice options.
    """
    
    def __init__(self, name: str = "ElevenLabsTTSAgent", **config):
        super().__init__(name, **config)
        self.capabilities = [
            AgentCapability.CONTENT_GENERATION,
            AgentCapability.AUDIO_PROCESSING,
            BrandCapability.VOICE_SYNTHESIS
        ]
        
        # Available voices (would be loaded from ElevenLabs API in production)
        self.available_voices = {
            "rachel": {"name": "Rachel", "description": "Professional female voice", "accent": "American"},
            "josh": {"name": "Josh", "description": "Clear male voice", "accent": "American"},
            "bella": {"name": "Bella", "description": "Friendly female voice", "accent": "American"},
            "arnold": {"name": "Arnold", "description": "Deep male voice", "accent": "American"},
            "adam": {"name": "Adam", "description": "Narrator male voice", "accent": "American"},
            "sam": {"name": "Sam", "description": "Young male voice", "accent": "American"},
            "antoni": {"name": "Antoni", "description": "Warm male voice", "accent": "American"},
            "domi": {"name": "Domi", "description": "Strong female voice", "accent": "American"}
        }
    
    async def execute(self, text: str, voice: str = "rachel", 
                     stability: float = 0.75, clarity: float = 0.75) -> AgentResponse:
        """
        Generate speech from text using ElevenLabs TTS.
        
        Args:
            text: Text to convert to speech
            voice: Voice ID or name
            stability: Voice stability (0.0-1.0)
            clarity: Voice clarity (0.0-1.0)
        
        Returns:
            Audio generation details and metadata
        """
        try:
            # Validate parameters
            if len(text) > 5000:
                return AgentResponse(
                    success=False,
                    error="Text too long. Maximum 5000 characters.",
                    result=None
                )
            
            if voice not in self.available_voices:
                voice = "rachel"  # Default fallback
            
            # Optimize text for TTS
            optimized_text = self._optimize_text_for_tts(text)
            
            # In production, this would call ElevenLabs API
            # For now, we'll provide comprehensive TTS analysis
            tts_analysis = await self._analyze_text_for_tts(optimized_text)
            
            return AgentResponse(
                success=True,
                result={
                    "tts_generation": {
                        "original_text": text,
                        "optimized_text": optimized_text,
                        "voice": self.available_voices[voice],
                        "settings": {
                            "stability": stability,
                            "clarity": clarity,
                            "style": "natural"
                        },
                        "analysis": tts_analysis,
                        "estimated_duration": f"{len(text.split()) * 0.6:.1f} seconds",
                        "estimated_cost": self._calculate_tts_cost(text),
                        "character_count": len(text),
                        "word_count": len(text.split())
                    },
                    "instructions": "Ready for ElevenLabs API integration",
                    "timestamp": datetime.now().isoformat()
                }
            )
                
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                result="TTS service unavailable"
            )
    
    def _optimize_text_for_tts(self, text: str) -> str:
        """Optimize text for better TTS output."""
        # Remove markdown formatting
        optimized = text.replace('**', '').replace('*', '').replace('_', '')
        
        # Expand common abbreviations
        abbreviations = {
            'AI': 'Artificial Intelligence',
            'API': 'Application Programming Interface',
            'UI': 'User Interface',
            'UX': 'User Experience',
            'CEO': 'Chief Executive Officer',
            'CTO': 'Chief Technology Officer',
            'etc.': 'etcetera',
            'e.g.': 'for example',
            'i.e.': 'that is'
        }
        
        for abbr, expansion in abbreviations.items():
            optimized = optimized.replace(abbr, expansion)
        
        # Add pauses for better pacing
        optimized = optimized.replace('.', '. ')
        optimized = optimized.replace(',', ', ')
        
        return optimized.strip()
    
    async def _analyze_text_for_tts(self, text: str) -> str:
        """Analyze text and provide TTS optimization suggestions."""
        analysis_prompt = f"""
        Analyze the following text for optimal text-to-speech conversion:

        Text: {text[:1000]}...

        Provide analysis on:
        1. Pronunciation challenges
        2. Pacing recommendations
        3. Emphasis suggestions
        4. Technical terms that need special handling
        5. Overall TTS readiness score (1-10)

        Keep analysis concise and actionable.
        """
        
        try:
            response = await self._safe_execute(analysis_prompt)
            return response.result if response.success else "Analysis unavailable"
        except:
            return "Basic TTS optimization applied"
    
    def _calculate_tts_cost(self, text: str) -> str:
        """Calculate estimated cost for TTS generation."""
        char_count = len(text)
        cost_per_char = 0.00015  # ElevenLabs approximate pricing
        total_cost = char_count * cost_per_char
        return f"${total_cost:.4f}"
    
    async def get_available_voices(self) -> AgentResponse:
        """Get list of available voices with details."""
        return AgentResponse(
            success=True,
            result={
                "voices": self.available_voices,
                "total_voices": len(self.available_voices),
                "voice_categories": {
                    "male": ["josh", "arnold", "adam", "sam", "antoni"],
                    "female": ["rachel", "bella", "domi"],
                    "professional": ["rachel", "josh", "adam"],
                    "casual": ["bella", "sam", "antoni"],
                    "authoritative": ["arnold", "domi"]
                }
            }
        )


class AdvancedImageGenerationAgent(GPTImageGenerationAgent):
    """
    Enhanced image generation agent with advanced prompt engineering
    and multiple style options for brand and marketing content.
    """
    
    def __init__(self, name: str = "AdvancedImageGenerationAgent", **config):
        super().__init__(name, **config)
        self.capabilities.extend([
            BrandCapability.VISUAL_CONTENT_CREATION,
            BrandCapability.BRAND_ASSET_GENERATION
        ])
        
        # Enhanced style presets
        self.style_presets = {
            "corporate": {
                "description": "Professional corporate style",
                "prompt_additions": "professional, corporate, clean, business-appropriate, high-quality photography style"
            },
            "startup": {
                "description": "Modern startup aesthetic",
                "prompt_additions": "modern, innovative, startup culture, tech-savvy, contemporary design"
            },
            "luxury": {
                "description": "Premium luxury brand style",
                "prompt_additions": "luxury, premium, elegant, sophisticated, high-end, exclusive"
            },
            "tech": {
                "description": "Technology and innovation focused",
                "prompt_additions": "futuristic, high-tech, digital, cyber, advanced technology, sci-fi elements"
            },
            "eco": {
                "description": "Sustainable and eco-friendly",
                "prompt_additions": "sustainable, eco-friendly, natural, green, organic, environmental"
            },
            "creative": {
                "description": "Artistic and creative expression",
                "prompt_additions": "artistic, creative, expressive, vibrant, imaginative, unique perspective"
            },
            "minimal": {
                "description": "Minimalist design approach",
                "prompt_additions": "minimalist, clean, simple, elegant, uncluttered, white space"
            }
        }
    
    async def execute(self, prompt: str, style: str = "professional", 
                     brand_context: Optional[str] = None, 
                     size: str = "1024x1024", quantity: int = 1) -> AgentResponse:
        """
        Enhanced image generation with brand context and style presets.
        
        Args:
            prompt: Base image description
            style: Style preset from available options
            brand_context: Additional brand context for consistency
            size: Image dimensions
            quantity: Number of variations
        
        Returns:
            Enhanced image generation plan with detailed creative brief
        """
        try:
            # Build enhanced prompt
            enhanced_prompt = self._build_enhanced_prompt(prompt, style, brand_context)
            
            # Generate creative brief
            creative_brief = await self._generate_creative_brief(enhanced_prompt, style)
            
            # Calculate technical specifications
            tech_specs = self._get_technical_specifications(size, quantity)
            
            return AgentResponse(
                success=True,
                result={
                    "image_generation_plan": {
                        "original_prompt": prompt,
                        "enhanced_prompt": enhanced_prompt,
                        "style_preset": self.style_presets.get(style, {"description": "Custom style"}),
                        "brand_context": brand_context,
                        "creative_brief": creative_brief,
                        "technical_specs": tech_specs,
                        "variations": [
                            f"Variation {i+1}: {enhanced_prompt} (angle {i+1})"
                            for i in range(quantity)
                        ],
                        "estimated_generation_time": f"{30 * quantity} seconds",
                        "quality_score": self._assess_prompt_quality(enhanced_prompt)
                    },
                    "production_ready": True,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Advanced image generation failed: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                result="Failed to generate image plan"
            )
    
    def _build_enhanced_prompt(self, prompt: str, style: str, brand_context: Optional[str]) -> str:
        """Build an enhanced prompt with style and brand context."""
        enhanced = prompt
        
        # Add style elements
        if style in self.style_presets:
            enhanced += f", {self.style_presets[style]['prompt_additions']}"
        
        # Add brand context
        if brand_context:
            enhanced += f", {brand_context}"
        
        # Add quality enhancers
        enhanced += ", masterpiece quality, detailed, professional photography"
        
        return enhanced
    
    async def _generate_creative_brief(self, prompt: str, style: str) -> str:
        """Generate a detailed creative brief for the image."""
        brief_prompt = f"""
        Create a detailed creative brief for image generation:

        Prompt: {prompt}
        Style: {style}

        Include:
        - Visual composition recommendations
        - Color palette suggestions
        - Lighting and mood direction
        - Technical photography notes
        - Brand consistency guidelines

        Keep it concise but comprehensive.
        """
        
        try:
            response = await self._safe_execute(brief_prompt)
            return response.result if response.success else "Standard creative brief applied"
        except:
            return f"Creative brief for {style} style imagery with professional composition"
    
    def _get_technical_specifications(self, size: str, quantity: int) -> Dict[str, Any]:
        """Get technical specifications for image generation."""
        dimensions = size.split('x')
        return {
            "resolution": size,
            "width": int(dimensions[0]),
            "height": int(dimensions[1]),
            "quantity": quantity,
            "aspect_ratio": f"{int(dimensions[0])/int(dimensions[1]):.2f}:1",
            "file_format": "PNG",
            "estimated_file_size": f"{int(dimensions[0]) * int(dimensions[1]) * 3 / 1024 / 1024:.1f}MB per image",
            "total_cost": self._calculate_cost(size, quantity)
        }
    
    def _assess_prompt_quality(self, prompt: str) -> Dict[str, Any]:
        """Assess the quality and effectiveness of the prompt."""
        word_count = len(prompt.split())
        specificity_score = min(word_count / 20, 1.0) * 10
        
        return {
            "specificity_score": f"{specificity_score:.1f}/10",
            "word_count": word_count,
            "quality_assessment": "High" if specificity_score > 7 else "Medium" if specificity_score > 4 else "Basic",
            "recommendations": "Good prompt structure" if specificity_score > 7 else "Consider adding more specific details"
        }


# Helper class for GPT Image results (matches the enhanced brand system)
@dataclass 
class GPTImage1Result:
    """Direct gpt-image-1 generation result"""
    success: bool
    image_data: Optional[str] = None  # Base64 encoded
    image_url: Optional[str] = None
    generation_metadata: Optional[Dict[str, Any]] = None
    processing_time: float = 0.0
    error_message: Optional[str] = None


# Export the main agent classes
__all__ = [
    'BrandDeconstructionAgent',
    'GPTImageGenerationAgent', 
    'BrandIntelligenceAgent',
    'BrandAnalysisRequest',
    'GPTImageRequest',
    'BrandIntelligenceReport'
]
