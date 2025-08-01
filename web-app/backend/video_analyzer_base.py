#!/usr/bin/env python3
"""
Base class for video understanding and analysis models
Provides a common interface for different video analysis implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json


class VideoAnalyzerBase(ABC):
    """Abstract base class for video analysis models"""
    
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the video analyzer
        
        Args:
            api_key: API key for the video analysis service
            **kwargs: Model-specific parameters
        """
        self.api_key = api_key
        self.model_name = self.__class__.__name__
        self.is_initialized = False
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the model and authenticate
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def upload_video(self, video_path: str) -> Optional[str]:
        """
        Upload video to the analysis service
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Video ID/reference for the uploaded video, or None if failed
        """
        pass
    
    @abstractmethod
    def analyze_video(self, 
                     video_ref: str, 
                     prompt: str, 
                     additional_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Analyze video with given prompt
        
        Args:
            video_ref: Video reference/ID from upload_video
            prompt: Analysis prompt/instructions
            additional_data: Optional additional context data (e.g., keypoints JSON)
            
        Returns:
            Analysis results dictionary or None if failed
            Expected format:
            {
                "analysis": str,  # Main analysis text
                "confidence": float,  # Optional confidence score
                "metadata": {
                    "model_name": str,
                    "processing_time": float,
                    "prompt_tokens": int,  # Optional
                    "response_tokens": int,  # Optional
                    ...
                },
                "structured_data": Dict[str, Any]  # Optional structured analysis
            }
        """
        pass
    
    @abstractmethod
    def cleanup_video(self, video_ref: str) -> bool:
        """
        Clean up uploaded video from the service
        
        Args:
            video_ref: Video reference to clean up
            
        Returns:
            True if cleanup successful, False otherwise
        """
        pass
    
    def validate_video_file(self, video_path: str) -> bool:
        """
        Validate if video file is supported
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if valid, False otherwise
        """
        path = Path(video_path)
        
        if not path.exists():
            return False
        
        if path.suffix.lower() not in self.supported_formats:
            return False
        
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model
        
        Returns:
            Dictionary containing model information
        """
        return {
            "name": self.model_name,
            "initialized": self.is_initialized,
            "supported_formats": self.supported_formats
        }
    
    def prepare_additional_data(self, 
                              keypoints_json: Optional[str] = None,
                              custom_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Prepare additional data for analysis
        
        Args:
            keypoints_json: Path to keypoints JSON file
            custom_data: Custom additional data
            
        Returns:
            Prepared additional data dictionary
        """
        additional_data = {}
        
        # Load keypoints data if provided
        if keypoints_json and Path(keypoints_json).exists():
            try:
                with open(keypoints_json, 'r') as f:
                    keypoints_data = json.load(f)
                additional_data["keypoints"] = keypoints_data
            except Exception as e:
                print(f"Warning: Failed to load keypoints data: {e}")
        
        # Add custom data
        if custom_data:
            additional_data.update(custom_data)
        
        return additional_data
    
    def cleanup(self):
        """Clean up resources"""
        self.is_initialized = False 