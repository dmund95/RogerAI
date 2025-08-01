#!/usr/bin/env python3
"""
Dummy Pose Estimator - Example implementation
This is a simple example showing how to implement a custom pose estimator
"""

import time
import random
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import cv2
from pose_estimator_base import PoseEstimatorBase


class DummyPoseEstimator(PoseEstimatorBase):
    """
    Dummy pose estimator for demonstration purposes
    Generates random keypoints for testing the modular system
    """
    
    def __init__(self, 
                 confidence_threshold: float = 0.5,
                 detection_probability: float = 0.8,
                 **kwargs):
        """
        Initialize dummy pose estimator
        
        Args:
            confidence_threshold: Minimum confidence for keypoints
            detection_probability: Probability of detecting a pose (0-1)
        """
        super().__init__(**kwargs)
        
        self.confidence_threshold = confidence_threshold
        self.detection_probability = detection_probability
        
        # Define simple keypoint structure (similar to COCO format)
        self.keypoint_names = [
            "nose", "left_eye", "right_eye", "left_ear", "right_ear",
            "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
            "left_wrist", "right_wrist", "left_hip", "right_hip",
            "left_knee", "right_knee", "left_ankle", "right_ankle"
        ]
        
        # Define connections for skeleton drawing
        self.skeleton_connections = [
            # Head
            (0, 1), (0, 2), (1, 3), (2, 4),  # nose to eyes, eyes to ears
            
            # Torso
            (5, 6), (5, 11), (6, 12), (11, 12),  # shoulders and hips
            
            # Left arm
            (5, 7), (7, 9),  # left shoulder to elbow to wrist
            
            # Right arm
            (6, 8), (8, 10),  # right shoulder to elbow to wrist
            
            # Left leg
            (11, 13), (13, 15),  # left hip to knee to ankle
            
            # Right leg
            (12, 14), (14, 16),  # right hip to knee to ankle
        ]
    
    def initialize(self) -> bool:
        """Initialize the dummy estimator"""
        print("Initializing Dummy Pose Estimator...")
        time.sleep(0.1)  # Simulate initialization time
        self.is_initialized = True
        return True
    
    def detect_pose(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Generate dummy pose keypoints
        
        Args:
            frame: Input frame
            
        Returns:
            Dummy pose data or None based on detection probability
        """
        if not self.is_initialized:
            return None
        
        start_time = time.time()
        
        # Simulate processing time
        time.sleep(0.001)  # 1ms processing time
        
        # Randomly decide if pose is detected
        if random.random() > self.detection_probability:
            return None
        
        h, w = frame.shape[:2]
        
        # Generate random keypoints
        keypoints = []
        for i, name in enumerate(self.keypoint_names):
            # Generate random position (roughly human-like proportions)
            if "eye" in name or name == "nose":
                # Face area (upper 20% of frame)
                x = random.uniform(0.3, 0.7)
                y = random.uniform(0.1, 0.3)
            elif "shoulder" in name or "elbow" in name or "wrist" in name:
                # Upper body area
                x = random.uniform(0.2, 0.8)
                y = random.uniform(0.2, 0.6)
            elif "hip" in name or "knee" in name or "ankle" in name:
                # Lower body area
                x = random.uniform(0.3, 0.7)
                y = random.uniform(0.4, 0.9)
            else:
                # Default area
                x = random.uniform(0.2, 0.8)
                y = random.uniform(0.2, 0.8)
            
            confidence = random.uniform(self.confidence_threshold, 1.0)
            
            keypoint = {
                "id": i,
                "name": name,
                "x": x,
                "y": y,
                "confidence": confidence,
                "pixel_x": int(x * w),
                "pixel_y": int(y * h)
            }
            keypoints.append(keypoint)
        
        # Calculate bounding box
        x_coords = [kp["pixel_x"] for kp in keypoints if kp["confidence"] > self.confidence_threshold]
        y_coords = [kp["pixel_y"] for kp in keypoints if kp["confidence"] > self.confidence_threshold]
        
        bbox = None
        if x_coords and y_coords:
            bbox = {
                "x": min(x_coords),
                "y": min(y_coords),
                "width": max(x_coords) - min(x_coords),
                "height": max(y_coords) - min(y_coords)
            }
        
        processing_time = time.time() - start_time
        
        pose_data = {
            "keypoints": keypoints,
            "bbox": bbox,
            "metadata": {
                "model_name": self.model_name,
                "processing_time": processing_time,
                "confidence_threshold": self.confidence_threshold,
                "frame_size": (w, h)
            }
        }
        
        return pose_data
    
    def draw_pose(self, frame: np.ndarray, pose_data: Dict[str, Any]) -> np.ndarray:
        """Draw dummy pose on frame"""
        if not pose_data or "keypoints" not in pose_data:
            return frame
        
        annotated_frame = frame.copy()
        keypoints = pose_data["keypoints"]
        
        # Draw connections
        for connection in self.skeleton_connections:
            start_idx, end_idx = connection
            if start_idx < len(keypoints) and end_idx < len(keypoints):
                start_kp = keypoints[start_idx]
                end_kp = keypoints[end_idx]
                
                if (start_kp["confidence"] > self.confidence_threshold and 
                    end_kp["confidence"] > self.confidence_threshold):
                    
                    start_point = (start_kp["pixel_x"], start_kp["pixel_y"])
                    end_point = (end_kp["pixel_x"], end_kp["pixel_y"])
                    
                    # Use different colors for different body parts
                    if start_idx <= 4:  # Head connections
                        color = (255, 0, 255)  # Magenta
                    elif start_idx <= 10:  # Arm connections
                        color = (0, 255, 255)  # Yellow
                    else:  # Leg connections
                        color = (255, 255, 0)  # Cyan
                    
                    cv2.line(annotated_frame, start_point, end_point, color, 2)
        
        # Draw keypoints
        for keypoint in keypoints:
            if keypoint["confidence"] > self.confidence_threshold:
                center = (keypoint["pixel_x"], keypoint["pixel_y"])
                
                # Color based on confidence
                confidence = keypoint["confidence"]
                if confidence > 0.8:
                    color = (0, 255, 0)  # Green for high confidence
                elif confidence > 0.6:
                    color = (0, 255, 255)  # Yellow for medium confidence
                else:
                    color = (0, 0, 255)  # Red for low confidence
                
                cv2.circle(annotated_frame, center, 5, color, -1)
                cv2.circle(annotated_frame, center, 7, (255, 255, 255), 2)
                
                # Draw keypoint name
                cv2.putText(annotated_frame, keypoint["name"], 
                           (center[0] + 10, center[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        
        # Draw bounding box
        if pose_data.get("bbox"):
            bbox = pose_data["bbox"]
            top_left = (bbox["x"], bbox["y"])
            bottom_right = (bbox["x"] + bbox["width"], bbox["y"] + bbox["height"])
            cv2.rectangle(annotated_frame, top_left, bottom_right, (128, 128, 128), 2)
        
        # Add model name to frame
        cv2.putText(annotated_frame, f"Model: {self.model_name}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return annotated_frame
    
    def get_keypoint_names(self) -> List[str]:
        """Get dummy keypoint names"""
        return self.keypoint_names.copy()
    
    def get_connections(self) -> List[Tuple[int, int]]:
        """Get dummy skeleton connections"""
        return self.skeleton_connections.copy()
    
    def cleanup(self):
        """Clean up dummy estimator"""
        print("Cleaning up Dummy Pose Estimator...")
        super().cleanup() 