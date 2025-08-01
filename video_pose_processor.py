#!/usr/bin/env python3
"""
Video Pose Processor
Processes videos using modular 2D human pose estimation models
"""

import cv2
import json
import numpy as np
import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import time

from model_factory import PoseEstimatorFactory
from pose_estimator_base import PoseEstimatorBase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VideoPoseProcessor:
    """Main class for processing videos with pose estimation"""
    
    def __init__(self, 
                 model_name: str = "mediapipe",
                 output_dir: str = "pose_output",
                 save_video: bool = True,
                 save_keypoints: bool = True,
                 **model_kwargs):
        """
        Initialize video pose processor
        
        Args:
            model_name: Name of the pose estimation model to use
            output_dir: Directory to save output files
            save_video: Whether to save annotated video
            save_keypoints: Whether to save keypoints JSON
            **model_kwargs: Arguments to pass to the pose estimation model
        """
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.save_video = save_video
        self.save_keypoints = save_keypoints
        self.model_kwargs = model_kwargs
        
        # Initialize pose estimator
        self.pose_estimator = PoseEstimatorFactory.create_estimator(model_name, **model_kwargs)
        if not self.pose_estimator:
            raise ValueError(f"Failed to create pose estimator: {model_name}")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize statistics
        self.stats = {
            "total_frames": 0,
            "frames_with_pose": 0,
            "total_processing_time": 0.0,
            "avg_fps": 0.0
        }
    
    def process_video(self, video_path: str) -> Dict[str, Any]:
        """
        Process a video file and extract pose keypoints
        
        Args:
            video_path: Path to input video file
            
        Returns:
            Dictionary containing processing results and statistics
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Initialize pose estimator
        if not self.pose_estimator.initialize():
            raise RuntimeError("Failed to initialize pose estimator")
        
        logger.info(f"Processing video: {video_path}")
        logger.info(f"Using model: {self.pose_estimator.model_name}")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")
        
        # Initialize video writer
        video_writer = None
        if self.save_video:
            output_video_path = self.output_dir / f"annotated_{Path(video_path).stem}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(str(output_video_path), fourcc, fps, (width, height))
            logger.info(f"Saving annotated video to: {output_video_path}")
        
        # Process frames
        frame_data = []
        frame_count = 0
        pose_detected_frames = 0
        start_time = time.time()
        
        logger.info("Starting video processing...")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_start_time = time.time()
                
                # Detect pose
                pose_data = self.pose_estimator.detect_pose(frame)
                
                frame_processing_time = time.time() - frame_start_time
                
                # Prepare frame info
                frame_info = {
                    "frame_number": frame_count,
                    "timestamp": frame_count / fps,
                    "pose_detected": pose_data is not None,
                    "processing_time": frame_processing_time
                }
                
                if pose_data:
                    frame_info["pose_data"] = pose_data
                    pose_detected_frames += 1
                    
                    # Draw pose on frame
                    if self.save_video:
                        annotated_frame = self.pose_estimator.draw_pose(frame, pose_data)
                        video_writer.write(annotated_frame)
                else:
                    frame_info["pose_data"] = None
                    if self.save_video:
                        video_writer.write(frame)
                
                frame_data.append(frame_info)
                frame_count += 1
                
                # Progress update
                if frame_count % 100 == 0 or frame_count == total_frames:
                    progress = (frame_count / total_frames) * 100
                    elapsed_time = time.time() - start_time
                    estimated_total = elapsed_time * total_frames / frame_count
                    remaining_time = estimated_total - elapsed_time
                    
                    logger.info(f"Progress: {frame_count}/{total_frames} ({progress:.1f}%) - "
                              f"Poses detected: {pose_detected_frames} - "
                              f"ETA: {remaining_time:.1f}s")
        
        finally:
            # Clean up
            cap.release()
            if video_writer:
                video_writer.release()
            self.pose_estimator.cleanup()
        
        # Calculate statistics
        total_processing_time = time.time() - start_time
        self.stats.update({
            "total_frames": total_frames,
            "frames_with_pose": pose_detected_frames,
            "total_processing_time": total_processing_time,
            "avg_fps": total_frames / total_processing_time if total_processing_time > 0 else 0,
            "pose_detection_rate": pose_detected_frames / total_frames if total_frames > 0 else 0
        })
        
        # Save keypoints data
        if self.save_keypoints:
            self._save_keypoints_data(video_path, frame_data, width, height, fps)
        
        logger.info(f"Processing complete! "
                   f"Pose detected in {pose_detected_frames}/{total_frames} frames "
                   f"({self.stats['pose_detection_rate']*100:.1f}%)")
        logger.info(f"Average processing speed: {self.stats['avg_fps']:.1f} FPS")
        
        return {
            "video_path": video_path,
            "output_directory": str(self.output_dir),
            "statistics": self.stats,
            "model_info": self.pose_estimator.get_model_info()
        }
    
    def _save_keypoints_data(self, video_path: str, frame_data: List[Dict], 
                           width: int, height: int, fps: int):
        """Save keypoints data to JSON file"""
        output_data = {
            "video_info": {
                "path": video_path,
                "width": width,
                "height": height,
                "fps": fps,
                "total_frames": len(frame_data)
            },
            "model_info": self.pose_estimator.get_model_info(),
            "processing_stats": self.stats,
            "frames": frame_data
        }
        
        keypoints_file = self.output_dir / f"keypoints_{Path(video_path).stem}.json"
        
        try:
            with open(keypoints_file, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            logger.info(f"Keypoints saved to: {keypoints_file}")
        except Exception as e:
            logger.error(f"Failed to save keypoints: {e}")
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get information about available models"""
        return PoseEstimatorFactory.get_available_models()
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        return PoseEstimatorFactory.get_model_info(model_name)


def main():
    """Main function for command line interface"""
    parser = argparse.ArgumentParser(description="Modular 2D Human Pose Estimation for Videos")
    
    # Required arguments
    parser.add_argument("video_path", help="Path to input video file")
    
    # Model selection
    parser.add_argument("--model", default="mediapipe", 
                       help="Pose estimation model to use (default: mediapipe)")
    
    # Output options
    parser.add_argument("--output_dir", default="pose_output",
                       help="Output directory for results (default: pose_output)")
    parser.add_argument("--no_video", action="store_true",
                       help="Skip saving annotated video")
    parser.add_argument("--no_keypoints", action="store_true",
                       help="Skip saving keypoints JSON")
    
    # MediaPipe specific options
    parser.add_argument("--model_complexity", type=int, default=1, choices=[0, 1, 2],
                       help="MediaPipe model complexity (0=fast, 1=balanced, 2=accurate)")
    parser.add_argument("--min_detection_confidence", type=float, default=0.5,
                       help="Minimum detection confidence (0.0-1.0)")
    parser.add_argument("--min_tracking_confidence", type=float, default=0.5,
                       help="Minimum tracking confidence (0.0-1.0)")
    
    args = parser.parse_args()
    
    # Check if model is supported
    if args.model.lower() not in PoseEstimatorFactory.get_available_models():
        logger.error(f"Model '{args.model}' is not supported")
        sys.exit(1)
    
    # Validate video file
    if not os.path.exists(args.video_path):
        logger.error(f"Video file not found: {args.video_path}")
        sys.exit(1)
    
    try:
        # Prepare model arguments
        model_kwargs = {}
        if args.model.lower() in ['mediapipe', 'mp']:
            model_kwargs.update({
                'model_complexity': args.model_complexity,
                'min_detection_confidence': args.min_detection_confidence,
                'min_tracking_confidence': args.min_tracking_confidence
            })
        
        # Create processor
        processor = VideoPoseProcessor(
            model_name=args.model,
            output_dir=args.output_dir,
            save_video=not args.no_video,
            save_keypoints=not args.no_keypoints,
            **model_kwargs
        )
        
        # Process video
        results = processor.process_video(args.video_path)
        
        # Print summary
        print("\n" + "="*60)
        print("PROCESSING SUMMARY")
        print("="*60)
        print(f"Video: {results['video_path']}")
        print(f"Model: {results['model_info']['name']}")
        print(f"Total frames: {results['statistics']['total_frames']}")
        print(f"Frames with pose: {results['statistics']['frames_with_pose']}")
        print(f"Detection rate: {results['statistics']['pose_detection_rate']*100:.1f}%")
        print(f"Processing speed: {results['statistics']['avg_fps']:.1f} FPS")
        print(f"Total time: {results['statistics']['total_processing_time']:.1f}s")
        print(f"Output directory: {results['output_directory']}")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 