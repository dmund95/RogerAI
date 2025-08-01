#!/usr/bin/env python3
"""
Example usage of the Modular Pose Estimation System
Demonstrates different ways to use the system
"""

import os
from pathlib import Path
from video_pose_processor import VideoPoseProcessor
from model_factory import PoseEstimatorFactory


def example_basic_usage():
    """Example 1: Basic video processing"""
    print("="*50)
    print("Example 1: Basic Video Processing")
    print("="*50)
    
    # Note: Replace with an actual video file path
    video_path = "path/to/your/video.mp4"
    
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        print("Please update the video_path variable with a valid video file.")
        return
    
    # Create processor with MediaPipe
    processor = VideoPoseProcessor(
        model_name="mediapipe",
        output_dir="example_output",
        model_complexity=1  # Balanced mode
    )
    
    # Process the video
    results = processor.process_video(video_path)
    
    print(f"✅ Processing complete!")
    print(f"📁 Results saved in: {results['output_directory']}")
    print(f"📊 Detection rate: {results['statistics']['pose_detection_rate']*100:.1f}%")


def example_model_comparison():
    """Example 2: Compare different models"""
    print("\n" + "="*50)
    print("Example 2: Model Comparison")
    print("="*50)
    
    video_path = "path/to/your/video.mp4"
    
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return
    
    models_to_test = ["mediapipe", "dummy"]
    
    for model_name in models_to_test:
        print(f"\n🔄 Testing model: {model_name}")
        
        processor = VideoPoseProcessor(
            model_name=model_name,
            output_dir=f"comparison_output/{model_name}",
            save_keypoints=True,
            save_video=True
        )
        
        results = processor.process_video(video_path)
        
        print(f"   ✅ {model_name}: {results['statistics']['pose_detection_rate']*100:.1f}% detection rate")
        print(f"   ⚡ {model_name}: {results['statistics']['avg_fps']:.1f} FPS")


def example_custom_settings():
    """Example 3: Custom model settings"""
    print("\n" + "="*50)
    print("Example 3: Custom Model Settings")
    print("="*50)
    
    video_path = "path/to/your/video.mp4"
    
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return
    
    # High accuracy MediaPipe settings
    processor = VideoPoseProcessor(
        model_name="mediapipe",
        output_dir="high_accuracy_output",
        model_complexity=2,  # Highest accuracy
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    
    results = processor.process_video(video_path)
    
    print(f"✅ High accuracy processing complete!")
    print(f"📊 Detection rate: {results['statistics']['pose_detection_rate']*100:.1f}%")
    print(f"⚡ Processing speed: {results['statistics']['avg_fps']:.1f} FPS")


def example_programmatic_model_info():
    """Example 4: Get model information programmatically"""
    print("\n" + "="*50)
    print("Example 4: Model Information")
    print("="*50)
    
    # List available models
    available_models = PoseEstimatorFactory.get_available_models()
    print("📋 Available models:")
    for name, model_class in available_models.items():
        print(f"   - {name}: {model_class.__name__}")
    
    # Get detailed info for each model
    for model_name in ["mediapipe", "dummy"]:
        print(f"\n🔍 Model info: {model_name}")
        info = PoseEstimatorFactory.get_model_info(model_name)
        if info:
            print(f"   Class: {info['class_name']}")
            print(f"   Keypoints: {info['num_keypoints']}")
            print(f"   First 5 keypoints: {info['keypoints'][:5]}")
            print(f"   Connections: {len(info['connections'])} skeleton connections")


def example_batch_processing():
    """Example 5: Batch processing multiple videos"""
    print("\n" + "="*50)
    print("Example 5: Batch Processing")
    print("="*50)
    
    # Example video directory (replace with actual path)
    video_dir = Path("path/to/video/directory")
    
    if not video_dir.exists():
        print(f"Video directory not found: {video_dir}")
        print("Please update the video_dir variable with a valid directory.")
        return
    
    # Find all video files
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    video_files = []
    for ext in video_extensions:
        video_files.extend(video_dir.glob(f"*{ext}"))
    
    if not video_files:
        print("No video files found in the directory.")
        return
    
    print(f"📁 Found {len(video_files)} video files")
    
    # Process each video
    for i, video_path in enumerate(video_files[:3]):  # Limit to first 3 for demo
        print(f"\n🔄 Processing {i+1}/{len(video_files)}: {video_path.name}")
        
        processor = VideoPoseProcessor(
            model_name="mediapipe",
            output_dir=f"batch_output/{video_path.stem}",
            model_complexity=1
        )
        
        try:
            results = processor.process_video(str(video_path))
            print(f"   ✅ Success: {results['statistics']['pose_detection_rate']*100:.1f}% detection")
        except Exception as e:
            print(f"   ❌ Error: {e}")


def example_single_frame_processing():
    """Example 6: Process a single frame"""
    print("\n" + "="*50)
    print("Example 6: Single Frame Processing")
    print("="*50)
    
    import cv2
    from model_factory import PoseEstimatorFactory
    
    # Create a test image (or load from file)
    # test_image = cv2.imread("path/to/image.jpg")
    test_image = None
    
    if test_image is None:
        print("No test image available. Creating a dummy image...")
        import numpy as np
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Create pose estimator
    estimator = PoseEstimatorFactory.create_estimator("mediapipe")
    
    if estimator and estimator.initialize():
        print("🔄 Processing single frame...")
        
        # Detect pose
        pose_data = estimator.detect_pose(test_image)
        
        if pose_data:
            print(f"✅ Pose detected with {len(pose_data['keypoints'])} keypoints")
            
            # Draw pose on image
            annotated_image = estimator.draw_pose(test_image, pose_data)
            
            # Save result
            cv2.imwrite("single_frame_result.jpg", annotated_image)
            print("💾 Result saved as 'single_frame_result.jpg'")
        else:
            print("❌ No pose detected in the frame")
        
        estimator.cleanup()
    else:
        print("❌ Failed to initialize pose estimator")


def main():
    """Run all examples"""
    print("🚀 Modular Pose Estimation System - Examples")
    print("=" * 60)
    
    # Run examples
    try:
        example_programmatic_model_info()
        example_single_frame_processing()
        
        # Video processing examples (commented out since they need actual video files)
        # example_basic_usage()
        # example_model_comparison()
        # example_custom_settings()
        # example_batch_processing()
        
        print("\n" + "="*60)
        print("✅ Examples completed!")
        print("\nTo run video processing examples:")
        print("1. Update video paths in the example functions")
        print("2. Uncomment the video processing examples in main()")
        print("3. Run the script again")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")


if __name__ == "__main__":
    main() 