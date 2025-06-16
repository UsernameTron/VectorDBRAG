#!/usr/bin/env python3
"""
Brand Deconstruction Service for NEXUS AI Platform
Scrapes websites and returns pentagram-formatted prompts for image generation
Incorporates ultra-fidelity modifiers from previous analysis
"""

import asyncio
import requests
from bs4 import BeautifulSoup
import openai
import os
import json
import time
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
import re

@dataclass
class PentagramPrompt:
    """Pentagram-formatted prompt structure following PENTAGRAM framework"""
    # Core essence
    center_essence: str
    
    # PENTAGRAM points
    physicality: str        # P - Physical/material attributes
    environment: str        # E - Spatial and lighting context  
    narrative: str          # N - Emotional/conceptual story
    texture: str           # T - Surface behavior and interaction
    atmosphere: str        # A - Lighting mood and color
    geometry: str          # G - Framing and camera parameters
    rendering: str         # R - Fidelity and technical specs
    art_direction: str     # A2 - Style and visual identity
    motion_absence: str    # M - Stillness specifications
    
    # Meta information
    brand_name: str = ""
    vulnerability_theme: str = ""
    satirical_angle: str = ""
    
    def to_ultra_fidelity_prompt(self) -> str:
        """Convert to ultra-high fidelity image generation prompt"""
        
        # Ultra-fidelity technical specs
        technical_specs = [
            "12K (12288×6480) resolution",
            "Path-traced global illumination", 
            "16-bit RAW pipeline",
            "Disney BRDF materials",
            "Zeiss Otus 85mm f/1.4",
            "ACES colorspace",
            "Zero artifacts"
        ]
        
        return f"""
BRAND DECONSTRUCTION ULTRA-FIDELITY PROMPT:

🎯 BRAND: {self.brand_name}
🔥 CORE ESSENCE: {self.center_essence}
⚡ SATIRICAL ANGLE: {self.satirical_angle}
🎭 VULNERABILITY: {self.vulnerability_theme}

PENTAGRAM FRAMEWORK:
P - PHYSICALITY: {self.physicality}
E - ENVIRONMENT: {self.environment} 
N - NARRATIVE: {self.narrative}
T - TEXTURE: {self.texture}
A - ATMOSPHERE: {self.atmosphere}
G - GEOMETRY: {self.geometry}
R - RENDERING: {self.rendering}
A - ART DIRECTION: {self.art_direction}
M - MOTION ABSENCE: {self.motion_absence}

TECHNICAL SPECIFICATIONS:
{', '.join(technical_specs)}

UNIFIED PROMPT:
{self._generate_unified_prompt()}

NEGATIVE PROMPTS:
No watermark, no text overlay, no UI elements, no cartoon style, no distortion, no artifacts
"""

    def _generate_unified_prompt(self) -> str:
        """Generate the main unified prompt for image generation"""
        return f"""A satirical brand deconstruction of {self.brand_name}: {self.center_essence}. {self.physicality} {self.environment} {self.narrative} Rendered with {self.texture} and {self.atmosphere}. {self.geometry} {self.art_direction} {self.motion_absence} {self.rendering}"""

class BrandDeconstructionService:
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.client = openai.OpenAI(api_key=openai_api_key)
        
        # Load ultra-fidelity modifiers if available
        self.ultra_fidelity_modifiers = self._load_ultra_fidelity_modifiers()
        
    def _load_ultra_fidelity_modifiers(self) -> Dict[str, List[str]]:
        """Load ultra-fidelity modifiers from JSON file"""
        try:
            # Check multiple possible locations
            possible_paths = [
                '/Users/cpconnor/Downloads/ultra_fidelity_modifiers.json',
                'ultra_fidelity_modifiers.json',
                'config/ultra_fidelity_modifiers.json'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        return json.load(f)
                        
            # Fallback defaults
            return {
                "resolution_render_engine": ["12K resolution", "Path-traced", "Global illumination"],
                "sensor_optics": ["Zeiss Otus 85mm f/1.4", "f/1.2 prime", "11-blade bokeh"],
                "material_surface_fidelity": ["PBR materials", "Subsurface scattering", "Fine detail"],
                "lighting_atmospherics": ["HDRI dome", "Volumetric fog", "Soft fill"],
                "art_direction": ["Corporate satire", "Minimal brutalism", "Subversive realism"]
            }
        except Exception:
            return {}
    
    def scrape_website(self, url: str) -> Dict[str, str]:
        """Scrape website content for brand analysis"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Extract brand name from title or URL
            brand_name = self._extract_brand_name(title_text, url)
            
            # Remove script and style elements
            for script in soup(["script", "style", "noscript"]):
                script.decompose()
                
            # Get main content using multiple strategies
            main_content = self._extract_main_content(soup)
            
            # Extract meta description and keywords safely
            description = ""
            keywords = ""
            
            # Try to extract description from meta tag
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                try:
                    description = str(meta_desc).split('content="')[1].split('"')[0] if 'content="' in str(meta_desc) else ""
                except (IndexError, AttributeError):
                    description = ""
            
            # Try to extract keywords from meta tag
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                try:
                    keywords = str(meta_keywords).split('content="')[1].split('"')[0] if 'content="' in str(meta_keywords) else ""
                except (IndexError, AttributeError):
                    keywords = ""
            
            return {
                'title': title_text,
                'brand_name': brand_name,
                'description': description,
                'keywords': keywords,
                'content': main_content[:2000],  # Limit content
                'url': url
            }
            
        except Exception as e:
            brand_name = self._extract_brand_name("", url)
            return {
                'title': f"Analysis of {brand_name}",
                'brand_name': brand_name,
                'description': f"Brand analysis requested for {url}",
                'keywords': "",
                'content': f"Unable to access website content. Domain: {brand_name}. Error: {str(e)}",
                'url': url
            }
    
    def _extract_brand_name(self, title: str, url: str) -> str:
        """Extract brand name from title or URL"""
        # Try to extract from title first
        if title:
            # Remove common suffixes
            clean_title = re.sub(r'\s*[-|–]\s*(Home|Homepage|Official Site|Welcome).*$', '', title, flags=re.IGNORECASE)
            if clean_title and len(clean_title) > 2:
                return clean_title.strip()
        
        # Extract from URL
        domain_match = re.search(r'https?://(?:www\.)?([^/.]+)', url)
        if domain_match:
            domain = domain_match.group(1)
            # Remove common TLDs and return capitalized
            brand = re.sub(r'\.(com|org|net|io|ai|co)$', '', domain, flags=re.IGNORECASE)
            return brand.capitalize()
        
        return "Unknown Brand"
    
    def _extract_main_content(self, soup) -> str:
        """Extract main content using multiple strategies"""
        content_parts = []
        
        # Strategy 1: Look for main content containers
        main_selectors = [
            'main', '[role="main"]', '.main-content', '#main-content',
            '.content', '#content', '.page-content', '.site-content'
        ]
        
        for selector in main_selectors:
            elements = soup.select(selector)
            if elements:
                content_parts.append(elements[0].get_text())
                break
        
        # Strategy 2: Look for hero/banner sections
        hero_selectors = [
            '.hero', '.banner', '.jumbotron', '.intro', 
            'h1', '.headline', '.page-title'
        ]
        
        for selector in hero_selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements[:2]:  # Take first 2 matches
                    text = elem.get_text().strip()
                    if len(text) > 10:  # Only meaningful content
                        content_parts.append(text)
                break
        
        # Strategy 3: Look for about/description sections
        about_selectors = [
            '.about', '.description', '.overview', '.summary',
            '[class*="about"]', '[class*="description"]'
        ]
        
        for selector in about_selectors:
            elements = soup.select(selector)
            if elements:
                content_parts.append(elements[0].get_text())
                break
        
        # Combine and clean content
        combined_content = ' '.join(content_parts)
        # Clean whitespace and return limited content
        return re.sub(r'\s+', ' ', combined_content).strip()
    
    async def analyze_brand_pentagram(self, website_data: Dict[str, str]) -> PentagramPrompt:
        """Analyze brand using PENTAGRAM framework"""
        
        analysis_prompt = f"""
You are an expert satirical brand deconstruction analyst. Analyze this website data and create a PENTAGRAM-formatted response for generating an ultra-high fidelity satirical image.

WEBSITE DATA:
Brand: {website_data['brand_name']}
Title: {website_data['title']}
Description: {website_data['description']}
Keywords: {website_data['keywords']}
Content: {website_data['content'][:1000]}
URL: {website_data['url']}

Create a PENTAGRAM analysis for ultra-fidelity image generation:

CORE ESSENCE: What is this brand's fundamental identity? Be satirically insightful but not crude.

PENTAGRAM FRAMEWORK (for image generation):
P - PHYSICALITY: Specific physical/material attributes (texture, surface, tangible elements)
E - ENVIRONMENT: Spatial context and lighting setup (background, setting, containment)  
N - NARRATIVE: Implied emotional story or conceptual theme (temporal cues, mood)
T - TEXTURE: Surface micro-behavior and light interaction (finish, layering, detail)
A - ATMOSPHERE: Lighting mood, color temperature, emotional tone (key/fill ratios)
G - GEOMETRY: Camera framing and composition (lens choice, angle, depth of field)
R - RENDERING: Technical fidelity requirements (resolution, ray tracing, quality)
A - ART DIRECTION: Visual style and artistic approach (design system, palette)
M - MOTION ABSENCE: Stillness specifications (frozen moment, zero movement)

SATIRICAL ANGLE: What specific corporate absurdity or pretension should be highlighted?
VULNERABILITY THEME: What gap between brand promise and reality should be exposed?

Keep each element concise (1-2 sentences) and focused on visual image generation specifications.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at satirical brand deconstruction and ultra-fidelity visual prompt creation using the PENTAGRAM framework."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=1200,
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            if content:
                # Parse the response into PENTAGRAM format
                result = self._parse_pentagram_response(content, website_data)
                return result
            else:
                # Fallback if no content
                return self._create_fallback_pentagram(website_data)
            
        except Exception as e:
            # Fallback PENTAGRAM if API fails
            return self._create_fallback_pentagram(website_data)
    
    def _parse_pentagram_response(self, content: str, website_data: Dict[str, str]) -> PentagramPrompt:
        """Parse AI response into PENTAGRAM structure"""
        
        def extract_section(pattern: str, content: str) -> str:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                text = match.group(1).strip()
                # Clean up the text
                text = re.sub(r'\s+', ' ', text)
                # Remove any trailing colons or dashes
                text = re.sub(r'^[:\-\s]+', '', text)
                return text
            return ""
        
        # More flexible extraction patterns
        essence = extract_section(r'(?:CORE ESSENCE|CENTER)[:\-]?\s*(.*?)(?=PENTAGRAM|P[\s\-]|$)', content)
        physicality = extract_section(r'P[\s\-].*?(?:PHYSICALITY|Physical)[:\-]?\s*(.*?)(?=E[\s\-]|$)', content)
        environment = extract_section(r'E[\s\-].*?(?:ENVIRONMENT|Environment)[:\-]?\s*(.*?)(?=N[\s\-]|$)', content)
        narrative = extract_section(r'N[\s\-].*?(?:NARRATIVE|Narrative)[:\-]?\s*(.*?)(?=T[\s\-]|$)', content)
        texture = extract_section(r'T[\s\-].*?(?:TEXTURE|Texture)[:\-]?\s*(.*?)(?=A[\s\-]|$)', content)
        atmosphere = extract_section(r'A[\s\-].*?(?:ATMOSPHERE|Atmosphere)[:\-]?\s*(.*?)(?=G[\s\-]|$)', content)
        geometry = extract_section(r'G[\s\-].*?(?:GEOMETRY|Geometry)[:\-]?\s*(.*?)(?=R[\s\-]|$)', content)
        rendering = extract_section(r'R[\s\-].*?(?:RENDERING|Rendering)[:\-]?\s*(.*?)(?=A[\s\-]|ART|$)', content)
        art_direction = extract_section(r'(?:A[\s\-].*?(?:ART|Art)|ART DIRECTION)[:\-]?\s*(.*?)(?=M[\s\-]|$)', content)
        motion = extract_section(r'M[\s\-].*?(?:MOTION|Motion)[:\-]?\s*(.*?)(?=SATIRICAL|VULNERABILITY|$)', content)
        
        satirical_angle = extract_section(r'(?:SATIRICAL ANGLE|SATIRICAL)[:\-]?\s*(.*?)(?=VULNERABILITY|$)', content)
        vulnerability = extract_section(r'(?:VULNERABILITY THEME|VULNERABILITY)[:\-]?\s*(.*?)$', content)
        
        # Fallback values using brand context
        brand_name = website_data['brand_name']
        fallback_essence = f"Corporate identity of {brand_name} with polished exterior hiding operational complexity"
        
        return PentagramPrompt(
            center_essence=essence or fallback_essence,
            physicality=physicality or f"Premium {brand_name} materials with subtle wear and authentic textures",
            environment=environment or f"Sterile {brand_name} corporate environment with controlled lighting revealing underlying operations",
            narrative=narrative or f"Moment of {brand_name} corporate theater interrupted by genuine human experience",
            texture=texture or f"Smooth {brand_name} corporate surfaces contrasted with underlying operational texture",
            atmosphere=atmosphere or f"Professional {brand_name} lighting with warm human elements bleeding through the corporate facade",
            geometry=geometry or f"Clean {brand_name} corporate framing with compositional elements suggesting deeper truths",
            rendering=rendering or "Ultra-high fidelity corporate photography with documentary realism and technical precision",
            art_direction=art_direction or f"{brand_name} corporate minimalism disrupted by authentic visual elements and subversive details",
            motion_absence=motion or f"Frozen {brand_name} corporate performance, suspended between polished image and operational reality",
            brand_name=brand_name,
            satirical_angle=satirical_angle or f"{brand_name} corporate perfectionism confronted by operational and human reality",
            vulnerability_theme=vulnerability or f"Gap between {brand_name} brand promise and actual customer experience"
        )
    
    def _create_fallback_pentagram(self, website_data: Dict[str, str]) -> PentagramPrompt:
        """Create fallback PENTAGRAM when AI analysis fails"""
        return PentagramPrompt(
            center_essence=f"Corporate brand identity of {website_data['brand_name']} - polished exterior hiding mundane reality",
            physicality="Premium materials with visible wear, corporate logos with subtle distortions",
            environment="Pristine corporate setting with everyday chaos bleeding through edges",
            narrative="Moment of corporate theater interrupted by authentic human experience",
            texture="Smooth corporate surfaces with underlying texture of real operations",
            atmosphere="Professional lighting revealing shadows of actual business practices",
            geometry="Clean corporate framing with compositional elements suggesting deeper truths",
            rendering="Ultra-high fidelity corporate photography with documentary realism",
            art_direction="Corporate minimalism disrupted by authentic visual elements",
            motion_absence="Frozen corporate performance, suspended between image and reality",
            brand_name=website_data['brand_name'],
            satirical_angle="Corporate perfectionism confronted by operational reality",
            vulnerability_theme="Brand promise versus customer experience disconnect"
        )
    
    async def deconstruct_brand(self, url: str) -> Dict[str, Any]:
        """Main method: scrape website and return PENTAGRAM analysis"""
        start_time = time.time()
        
        try:
            # Step 1: Scrape website
            website_data = self.scrape_website(url)
            
            # Step 2: Analyze using PENTAGRAM framework
            pentagram = await self.analyze_brand_pentagram(website_data)
            
            # Step 3: Generate ultra-fidelity prompt
            ultra_prompt = pentagram.to_ultra_fidelity_prompt()
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'brand_name': website_data['brand_name'],
                'website_data': website_data,
                'pentagram_analysis': asdict(pentagram),
                'ultra_fidelity_prompt': ultra_prompt,
                'processing_time': round(processing_time, 2),
                'timestamp': time.time(),
                'analysis_id': f"brand_analysis_{int(time.time())}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time,
                'timestamp': time.time()
            }

# Export for use in other modules
__all__ = ['BrandDeconstructionService', 'PentagramPrompt']
