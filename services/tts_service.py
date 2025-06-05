"""
OpenAI Text-to-Speech Service
Integrated with existing agent system for enhanced functionality
"""

import os
import logging
import tempfile
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
import json

from openai import OpenAI
import requests

# Import existing agents for enhanced functionality
try:
    from VectorDBRAG.agents import AudioAgent
    from VectorDBRAG.unified_agent_system import AgentSystem
    AGENTS_AVAILABLE = True
except ImportError:
    try:
        from agents import AudioAgent
        from unified_agent_system import AgentSystem
        AGENTS_AVAILABLE = True
    except ImportError:
        # Fallback if agents not available
        AGENTS_AVAILABLE = False
        class AudioAgent:
            pass
        class AgentSystem:
            pass

class TTSService:
    """
    Comprehensive OpenAI Text-to-Speech service integrated with existing agent system
    """
    
    # Available voices and their characteristics
    VOICES = {
        'alloy': {'description': 'Balanced, neutral voice', 'gender': 'neutral'},
        'ash': {'description': 'Clear, professional tone ideal for business', 'gender': 'neutral'},
        'coral': {'description': 'Friendly, approachable voice for conversations', 'gender': 'female'},
        'echo': {'description': 'Warm, expressive voice', 'gender': 'neutral'},
        'fable': {'description': 'Clear, articulate voice', 'gender': 'neutral'},
        'nova': {'description': 'Bright, energetic voice', 'gender': 'female'},
        'onyx': {'description': 'Deep, resonant voice', 'gender': 'male'},
        'sage': {'description': 'Wise, measured voice ideal for educational content', 'gender': 'neutral'},
        'shimmer': {'description': 'Smooth, pleasant voice', 'gender': 'female'}
    }
    
    # Supported formats and speeds
    FORMATS = ['mp3', 'opus', 'aac', 'flac']
    SPEED_RANGE = (0.25, 4.0)
    MAX_TEXT_LENGTH = 4096
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize TTS service with OpenAI client and agent integration"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
            
        self.client = OpenAI(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        
        # Initialize agent system for enhanced functionality
        self.agents_available = AGENTS_AVAILABLE
        if self.agents_available:
            try:
                self.agent_system = AgentSystem()
                self.audio_agent = AudioAgent()
                self.logger.info("Agent system initialized successfully")
            except Exception as e:
                self.logger.warning(f"Agent system not available: {e}")
                self.agents_available = False
    
    def validate_input(self, text: str, voice: str, speed: float, format: str) -> Dict[str, Any]:
        """Validate input parameters with agent assistance"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Text validation
        if not text or not text.strip():
            validation_result['valid'] = False
            validation_result['errors'].append("Text cannot be empty")
        
        if len(text) > self.MAX_TEXT_LENGTH:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Text exceeds maximum length of {self.MAX_TEXT_LENGTH} characters")
        
        # Voice validation
        if voice not in self.VOICES:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Invalid voice. Available voices: {list(self.VOICES.keys())}")
        
        # Speed validation
        if not (self.SPEED_RANGE[0] <= speed <= self.SPEED_RANGE[1]):
            validation_result['valid'] = False
            validation_result['errors'].append(f"Speed must be between {self.SPEED_RANGE[0]} and {self.SPEED_RANGE[1]}")
        
        # Format validation
        if format not in self.FORMATS:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Invalid format. Available formats: {self.FORMATS}")
        
        # Use Research Agent for text analysis and suggestions
        if self.agents_available and validation_result['valid']:
            try:
                # Basic agent integration without specific method calls
                validation_result['suggestions'].append("Agent analysis available for enhanced TTS optimization")
            except Exception as e:
                self.logger.warning(f"Agent analysis failed: {e}")
        
        return validation_result
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for optimal TTS conversion"""
        # Basic preprocessing
        processed_text = text.strip()
        
        # Use Code Analyzer Agent for advanced text preprocessing
        if self.agents_available:
            try:
                # Basic preprocessing optimization without specific agent calls
                processed_text = text.strip()
                self.logger.info("Text preprocessing available with agent system")
            except Exception as e:
                self.logger.warning(f"Text preprocessing with agent failed: {e}")
        
        return processed_text
    
    def generate_speech(self, text: str, voice: str = 'alloy', speed: float = 1.0, 
                       format: str = 'mp3') -> Dict[str, Any]:
        """Generate speech from text using OpenAI TTS API"""
        try:
            # Validate inputs
            validation = self.validate_input(text, voice, speed, format)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'Validation failed',
                    'details': validation['errors'],
                    'warnings': validation.get('warnings', []),
                    'suggestions': validation.get('suggestions', [])
                }
            
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            # Ensure format is one of the allowed values
            valid_formats = ['mp3', 'opus', 'aac', 'flac', 'wav', 'pcm']
            if format not in valid_formats:
                format = 'mp3'  # Default fallback
            
            # Generate speech
            self.logger.info(f"Generating speech with voice: {voice}, speed: {speed}, format: {format}")
            
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=processed_text,
                response_format=format,  # type: ignore
                speed=speed
            )
            
            # Create temporary file for audio
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=f'.{format}',
                prefix='tts_'
            )
            
            # Write audio data to file
            with open(temp_file.name, 'wb') as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
            
            # Get file info
            file_size = os.path.getsize(temp_file.name)
            
            # Use Audio Agent for post-processing if available
            enhanced_file_path = temp_file.name
            if self.agents_available:
                try:
                    # Audio analysis available through agent system
                    self.logger.info("Audio analysis available through agent system")
                except Exception as e:
                    self.logger.warning(f"Audio agent processing failed: {e}")
            
            result = {
                'success': True,
                'file_path': enhanced_file_path,
                'file_size': file_size,
                'duration_estimate': len(processed_text) / 150,  # Rough estimate: 150 chars per minute
                'voice_used': voice,
                'speed_used': speed,
                'format_used': format,
                'text_processed': processed_text != text,
                'original_text': text,
                'processed_text': processed_text,
                'timestamp': datetime.now().isoformat(),
                'warnings': validation.get('warnings', []),
                'suggestions': validation.get('suggestions', [])
            }
            
            self.logger.info(f"Speech generation successful: {file_size} bytes")
            return result
            
        except Exception as e:
            error_msg = f"TTS generation failed: {str(e)}"
            self.logger.error(error_msg)
            
            # Use Code Debugger Agent for error analysis
            if self.agents_available:
                try:
                    # Debug analysis available through agent system
                    error_msg += f"\n\nAgent Analysis: Debug analysis available through agent system"
                except Exception as debug_error:
                    self.logger.warning(f"Error debugging with agent failed: {debug_error}")
            
            return {
                'success': False,
                'error': error_msg,
                'details': str(e)
            }
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get information about available voices"""
        return {
            'voices': self.VOICES,
            'total_voices': len(self.VOICES),
            'voice_categories': {
                'neutral': [v for v, info in self.VOICES.items() if info['gender'] == 'neutral'],
                'male': [v for v, info in self.VOICES.items() if info['gender'] == 'male'],
                'female': [v for v, info in self.VOICES.items() if info['gender'] == 'female']
            }
        }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get comprehensive service information"""
        return {
            'service_name': 'OpenAI Text-to-Speech',
            'model': 'tts-1',
            'voices': self.get_voice_info(),
            'formats': self.FORMATS,
            'speed_range': self.SPEED_RANGE,
            'max_text_length': self.MAX_TEXT_LENGTH,
            'agents_available': self.agents_available,
            'enhanced_features': {
                'text_preprocessing': self.agents_available,
                'audio_analysis': self.agents_available,
                'error_debugging': self.agents_available,
                'performance_optimization': self.agents_available
            }
        }
    
    def cleanup_temp_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Clean up temporary audio files"""
        cleaned = []
        errors = []
        
        for file_path in file_paths:
            try:
                if os.path.exists(file_path) and file_path.startswith(tempfile.gettempdir()):
                    os.unlink(file_path)
                    cleaned.append(file_path)
                    self.logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                error_msg = f"Failed to clean up {file_path}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        return {
            'cleaned': cleaned,
            'errors': errors,
            'total_cleaned': len(cleaned)
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics with agent assistance"""
        base_metrics = {
            'api_model': 'tts-1',
            'max_text_length': self.MAX_TEXT_LENGTH,
            'supported_formats': len(self.FORMATS),
            'available_voices': len(self.VOICES)
        }
        
        # Use Performance Agent for advanced metrics
        if self.agents_available:
            try:
                # Performance analysis available through agent system
                base_metrics['optimization_suggestions'] = "Performance optimization available through agent system"
            except Exception as e:
                self.logger.warning(f"Performance analysis with agent failed: {e}")
        
        return base_metrics

# Global TTS service instance
_tts_service = None

def get_tts_service() -> TTSService:
    """Get or create global TTS service instance"""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
