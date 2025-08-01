#!/usr/bin/env python3
"""
Factory for creating pose estimation models
Provides easy access to different model implementations
"""

from typing import Dict, Any, Optional
from pose_estimator_base import PoseEstimatorBase
from models.mediapipe_estimator import MediaPipePoseEstimator
from models.dummy_estimator import DummyPoseEstimator


class PoseEstimatorFactory:
    """Factory class for creating pose estimation models"""
    
    # Registry of available models
    _models = {
        'mediapipe': MediaPipePoseEstimator,
        'mp': MediaPipePoseEstimator,  # Alias
        'dummy': DummyPoseEstimator,
        'test': DummyPoseEstimator,  # Alias for testing
    }
    
    @classmethod
    def create_estimator(cls, model_name: str, **kwargs) -> Optional[PoseEstimatorBase]:
        """
        Create a pose estimator instance
        
        Args:
            model_name: Name of the model to create
            **kwargs: Model-specific parameters
            
        Returns:
            PoseEstimatorBase instance or None if model not found
        """
        model_name = model_name.lower()
        
        if model_name not in cls._models:
            print(f"Unknown model: {model_name}")
            print(f"Available models: {list(cls._models.keys())}")
            return None
        
        model_class = cls._models[model_name]
        return model_class(**kwargs)
    
    @classmethod
    def register_model(cls, name: str, model_class: type):
        """
        Register a new model class
        
        Args:
            name: Name to register the model under
            model_class: Model class that inherits from PoseEstimatorBase
        """
        if not issubclass(model_class, PoseEstimatorBase):
            raise ValueError("Model class must inherit from PoseEstimatorBase")
        
        cls._models[name.lower()] = model_class
        print(f"Registered model: {name}")
    
    @classmethod
    def get_available_models(cls) -> Dict[str, type]:
        """Get dictionary of available models"""
        return cls._models.copy()
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary with model information or None if not found
        """
        model_name = model_name.lower()
        
        if model_name not in cls._models:
            return None
        
        model_class = cls._models[model_name]
        
        # Create temporary instance to get info
        temp_instance = model_class()
        info = {
            'class_name': model_class.__name__,
            'module': model_class.__module__,
            'keypoints': temp_instance.get_keypoint_names(),
            'num_keypoints': len(temp_instance.get_keypoint_names()),
            'connections': temp_instance.get_connections()
        }
        
        return info


# Example of how to add a new model:
# 
# from models.your_custom_estimator import YourCustomPoseEstimator
# PoseEstimatorFactory.register_model('custom', YourCustomPoseEstimator) 