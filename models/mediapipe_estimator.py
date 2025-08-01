#!/usr/bin/env python3
"""
MediaPipe Pose implementation of the PoseEstimatorBase
"""

import time
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import cv2
import mediapipe as mp
from pose_estimator_base import PoseEstimatorBase


class MediaPipePoseEstimator(PoseEstimatorBase):
    """MediaPipe Pose implementation"""
    
    def __init__(self, 
                 static_image_mode: bool = False,
                 model_complexity: int = 1,
                 smooth_landmarks: bool = True,
                 enable_segmentation: bool = False,
                 smooth_segmentation: bool = True,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5,
                 **kwargs):
        """
        Initialize MediaPipe Pose estimator
        
        Args:
            static_image_mode: Whether to treat input as static image
            model_complexity: Model complexity (0, 1, or 2)
            smooth_landmarks: Whether to smooth landmarks
            enable_segmentation: Whether to enable segmentation
            smooth_segmentation: Whether to smooth segmentation
            min_detection_confidence: Minimum confidence for detection
            min_tracking_confidence: Minimum confidence for tracking
        """
        super().__init__(**kwargs)
        
        self.static_image_mode = static_image_mode
        self.model_complexity = model_complexity
        self.smooth_landmarks = smooth_landmarks
        self.enable_segmentation = enable_segmentation
        self.smooth_segmentation = smooth_segmentation
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        self.mp_pose = None
        self.mp_drawing = None
        self.mp_drawing_styles = None
        self.pose = None
        
        # MediaPipe Pose landmarks mapping
        self.landmark_names = [
            "nose",
            "left_eye_inner", "left_eye", "left_eye_outer",
            "right_eye_inner", "right_eye", "right_eye_outer",
            "left_ear", "right_ear",
            "mouth_left", "mouth_right",
            "left_shoulder", "right_shoulder",
            "left_elbow", "right_elbow",
            "left_wrist", "right_wrist",
            "left_pinky", "right_pinky",
            "left_index", "right_index",
            "left_thumb", "right_thumb",
            "left_hip", "right_hip",
            "left_knee", "right_knee",
            "left_ankle", "right_ankle",
            "left_heel", "right_heel",
            "left_foot_index", "right_foot_index"
        ]
        
        # MediaPipe pose connections
        self.pose_connections = [
            # Face
            (0, 1), (1, 2), (2, 3), (3, 7),  # Left eye to ear
            (0, 4), (4, 5), (5, 6), (6, 8),  # Right eye to ear
            (9, 10),  # Mouth
            
            # Torso
            (11, 12),  # Shoulders
            (11, 23), (12, 24),  # Shoulders to hips
            (23, 24),  # Hips
            
            # Left arm
            (11, 13), (13, 15),  # Shoulder to wrist
            (15, 17), (15, 19), (15, 21),  # Wrist to fingers
            (17, 19),  # Pinky to index
            
            # Right arm
            (12, 14), (14, 16),  # Shoulder to wrist
            (16, 18), (16, 20), (16, 22),  # Wrist to fingers
            (18, 20),  # Pinky to index
            
            # Left leg
            (23, 25), (25, 27),  # Hip to ankle
            (27, 29), (27, 31),  # Ankle to foot
            
            # Right leg
            (24, 26), (26, 28),  # Hip to ankle
            (28, 30), (28, 32),  # Ankle to foot
        ]
    
    def initialize(self) -> bool:
        """Initialize MediaPipe Pose"""
        try:
            self.mp_pose = mp.solutions.pose
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_drawing_styles = mp.solutions.drawing_styles
            
            self.pose = self.mp_pose.Pose(
                static_image_mode=self.static_image_mode,
                model_complexity=self.model_complexity,
                smooth_landmarks=self.smooth_landmarks,
                enable_segmentation=self.enable_segmentation,
                smooth_segmentation=self.smooth_segmentation,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            )
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"Failed to initialize MediaPipe Pose: {e}")
            return False
    
    def detect_pose(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """Detect pose using MediaPipe"""
        if not self.is_initialized:
            return None
        
        start_time = time.time()
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.pose.process(rgb_frame)
        
        processing_time = time.time() - start_time
        
        if not results.pose_landmarks:
            return None
        
        # Extract keypoints
        keypoints = []
        h, w = frame.shape[:2]
        
        for i, landmark in enumerate(results.pose_landmarks.landmark):
            keypoint = {
                "id": i,
                "name": self.landmark_names[i],
                "x": landmark.x,  # Normalized coordinates
                "y": landmark.y,
                "z": landmark.z,
                "confidence": landmark.visibility,
                "pixel_x": int(landmark.x * w),  # Pixel coordinates
                "pixel_y": int(landmark.y * h)
            }
            keypoints.append(keypoint)
        
        # Calculate bounding box
        x_coords = [kp["pixel_x"] for kp in keypoints if kp["confidence"] > 0.5]
        y_coords = [kp["pixel_y"] for kp in keypoints if kp["confidence"] > 0.5]
        
        bbox = None
        if x_coords and y_coords:
            bbox = {
                "x": min(x_coords),
                "y": min(y_coords),
                "width": max(x_coords) - min(x_coords),
                "height": max(y_coords) - min(y_coords)
            }
        
        pose_data = {
            "keypoints": keypoints,
            "bbox": bbox,
            "metadata": {
                "model_name": self.model_name,
                "processing_time": processing_time,
                "model_complexity": self.model_complexity,
                "frame_size": (w, h)
            }
        }
        
        return pose_data
    
    def draw_pose(self, frame: np.ndarray, pose_data: Dict[str, Any]) -> np.ndarray:
        """Draw pose on frame using MediaPipe style"""
        if not pose_data or "keypoints" not in pose_data:
            return frame
        
        annotated_frame = frame.copy()
        keypoints = pose_data["keypoints"]
        
        # Draw connections
        for connection in self.pose_connections:
            start_idx, end_idx = connection
            if start_idx < len(keypoints) and end_idx < len(keypoints):
                start_kp = keypoints[start_idx]
                end_kp = keypoints[end_idx]
                
                # Only draw if both keypoints are confident
                if start_kp["confidence"] > 0.5 and end_kp["confidence"] > 0.5:
                    start_point = (start_kp["pixel_x"], start_kp["pixel_y"])
                    end_point = (end_kp["pixel_x"], end_kp["pixel_y"])
                    
                    cv2.line(annotated_frame, start_point, end_point, (0, 255, 0), 2)
        
        # Draw keypoints
        for keypoint in keypoints:
            if keypoint["confidence"] > 0.5:
                center = (keypoint["pixel_x"], keypoint["pixel_y"])
                
                # Color based on keypoint type
                if "eye" in keypoint["name"] or keypoint["name"] == "nose":
                    color = (255, 0, 0)  # Blue for face
                elif "shoulder" in keypoint["name"] or "elbow" in keypoint["name"] or "wrist" in keypoint["name"]:
                    color = (0, 255, 0)  # Green for arms
                elif "hip" in keypoint["name"] or "knee" in keypoint["name"] or "ankle" in keypoint["name"]:
                    color = (0, 0, 255)  # Red for legs
                else:
                    color = (255, 255, 0)  # Cyan for others
                
                cv2.circle(annotated_frame, center, 4, color, -1)
                cv2.circle(annotated_frame, center, 6, (255, 255, 255), 2)
        
        # Draw bounding box if available
        # if pose_data.get("bbox"):
        #     bbox = pose_data["bbox"]
        #     top_left = (bbox["x"], bbox["y"])
        #     bottom_right = (bbox["x"] + bbox["width"], bbox["y"] + bbox["height"])
        #     cv2.rectangle(annotated_frame, top_left, bottom_right, (255, 255, 255), 2)
        
        return annotated_frame
    
    def get_keypoint_names(self) -> List[str]:
        """Get MediaPipe keypoint names"""
        return self.landmark_names.copy()
    
    def get_connections(self) -> List[Tuple[int, int]]:
        """Get MediaPipe pose connections"""
        return self.pose_connections.copy()
    
    def cleanup(self):
        """Clean up MediaPipe resources"""
        if self.pose:
            self.pose.close()
        super().cleanup() 