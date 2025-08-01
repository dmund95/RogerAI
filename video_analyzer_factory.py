#!/usr/bin/env python3
"""
Factory for creating video analysis models
Provides easy access to different video understanding implementations
"""

from typing import Dict, Any, Optional
from video_analyzer_base import VideoAnalyzerBase
from analyzers.gemini_analyzer import GeminiVideoAnalyzer


class VideoAnalyzerFactory:
    """Factory class for creating video analysis models"""
    
    # Registry of available analyzers
    _analyzers = {
        'gemini': GeminiVideoAnalyzer,
        'gemini-2.0-flash-exp': GeminiVideoAnalyzer,
        'gemini-2.5-pro': GeminiVideoAnalyzer,
        'google': GeminiVideoAnalyzer,  # Alias
    }
    
    @classmethod
    def create_analyzer(cls, analyzer_name: str, api_key: str, **kwargs) -> Optional[VideoAnalyzerBase]:
        """
        Create a video analyzer instance
        
        Args:
            analyzer_name: Name of the analyzer to create
            api_key: API key for the service
            **kwargs: Analyzer-specific parameters
            
        Returns:
            VideoAnalyzerBase instance or None if analyzer not found
        """
        analyzer_name = analyzer_name.lower()
        
        if analyzer_name not in cls._analyzers:
            print(f"Unknown analyzer: {analyzer_name}")
            print(f"Available analyzers: {list(cls._analyzers.keys())}")
            return None
        
        analyzer_class = cls._analyzers[analyzer_name]
        
        # Handle model-specific parameters
        if analyzer_name in ['gemini-2.5-pro']:
            kwargs.setdefault('model_name', 'gemini-2.5-pro')
        elif analyzer_name in ['gemini-2.0-flash-exp']:
            kwargs.setdefault('model_name', 'gemini-2.0-flash-exp')
        
        return analyzer_class(api_key=api_key, **kwargs)
    
    @classmethod
    def register_analyzer(cls, name: str, analyzer_class: type):
        """
        Register a new analyzer class
        
        Args:
            name: Name to register the analyzer under
            analyzer_class: Analyzer class that inherits from VideoAnalyzerBase
        """
        if not issubclass(analyzer_class, VideoAnalyzerBase):
            raise ValueError("Analyzer class must inherit from VideoAnalyzerBase")
        
        cls._analyzers[name.lower()] = analyzer_class
        print(f"Registered analyzer: {name}")
    
    @classmethod
    def get_available_analyzers(cls) -> Dict[str, type]:
        """Get dictionary of available analyzers"""
        return cls._analyzers.copy()
    
    @classmethod
    def get_analyzer_info(cls, analyzer_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific analyzer
        
        Args:
            analyzer_name: Name of the analyzer
            
        Returns:
            Dictionary with analyzer information or None if not found
        """
        analyzer_name = analyzer_name.lower()
        
        if analyzer_name not in cls._analyzers:
            return None
        
        analyzer_class = cls._analyzers[analyzer_name]
        
        info = {
            'class_name': analyzer_class.__name__,
            'module': analyzer_class.__module__,
            'description': analyzer_class.__doc__ or "No description available"
        }
        
        return info


# Example of how to add a new analyzer:
# 
# from analyzers.your_custom_analyzer import YourCustomVideoAnalyzer
# VideoAnalyzerFactory.register_analyzer('custom', YourCustomVideoAnalyzer) 