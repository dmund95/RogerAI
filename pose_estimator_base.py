#!/usr/bin/env python3
"""
Base class for 2D human pose estimation models
Provides a common interface for different pose estimation implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import cv2


class PoseEstimatorBase(ABC):
    """Abstract base class for pose estimation models"""
    
    def __init__(self, **kwargs):
        """Initialize the pose estimator with model-specific parameters"""
        self.model_name = self.__class__.__name__
        self.is_initialized = False
        
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the model and load weights
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def detect_pose(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Detect pose keypoints in a single frame
        
        Args:
            frame: Input frame as numpy array (BGR format)
            
        Returns:
            Dictionary containing pose data or None if no pose detected
            Expected format:
            {
                "keypoints": [
                    {
                        "id": int,
                        "name": str,
                        "x": float,  # normalized or pixel coordinates
                        "y": float,
                        "confidence": float  # 0-1
                    },
                    ...
                ],
                "bbox": {  # optional bounding box
                    "x": float,
                    "y": float,
                    "width": float,
                    "height": float
                },
                "metadata": {  # model-specific metadata
                    "model_name": str,
                    "processing_time": float,
                    ...
                }
            }
        """
        pass
    
    @abstractmethod
    def draw_pose(self, frame: np.ndarray, pose_data: Dict[str, Any]) -> np.ndarray:
        """
        Draw pose keypoints and connections on the frame
        
        Args:
            frame: Input frame
            pose_data: Pose data from detect_pose method
            
        Returns:
            Frame with pose visualization
        """
        pass
    
    @abstractmethod
    def get_keypoint_names(self) -> List[str]:
        """
        Get list of keypoint names in order
        
        Returns:
            List of keypoint names
        """
        pass
    
    @abstractmethod
    def get_connections(self) -> List[Tuple[int, int]]:
        """
        Get list of keypoint connections for drawing skeleton
        
        Returns:
            List of tuples representing connections between keypoint indices
        """
        pass
    
    def cleanup(self):
        """Clean up resources"""
        self.is_initialized = False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model
        
        Returns:
            Dictionary containing model information
        """
        return {
            "name": self.model_name,
            "initialized": self.is_initialized,
            "keypoints": self.get_keypoint_names(),
            "num_keypoints": len(self.get_keypoint_names())
        }
    
    def validate_pose_data(self, pose_data: Dict[str, Any]) -> bool:
        """
        Validate pose data format
        
        Args:
            pose_data: Pose data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(pose_data, dict):
            return False
        
        if "keypoints" not in pose_data:
            return False
        
        keypoints = pose_data["keypoints"]
        if not isinstance(keypoints, list):
            return False
        
        # Validate each keypoint
        for kp in keypoints:
            if not isinstance(kp, dict):
                return False
            required_fields = ["id", "name", "x", "y", "confidence"]
            if not all(field in kp for field in required_fields):
                return False
        
        return True 