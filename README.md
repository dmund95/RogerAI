# Modular 2D Human Pose Estimation System

A flexible and extensible system for 2D human pose estimation on videos. The system is designed with modularity in mind, allowing you to easily plug in different pose estimation models.

## Features

- **Modular Architecture**: Easy to add new pose estimation models
- **Multiple Model Support**: Currently supports MediaPipe Pose with easy extensibility
- **Video Processing**: Processes videos frame by frame with pose detection
- **Annotated Output**: Saves videos with pose keypoints visualized
- **Data Export**: Exports keypoint data as JSON for further analysis
- **Progress Tracking**: Real-time processing progress and statistics
- **Command Line Interface**: Easy to use CLI with configurable options

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```bash
# Process a video with MediaPipe Pose
python video_pose_processor.py path/to/your/video.mp4

# Use high accuracy mode
python video_pose_processor.py path/to/your/video.mp4 --model-complexity 2

# Use dummy model for testing
python video_pose_processor.py path/to/your/video.mp4 --model dummy
```

### List Available Models

```bash
python video_pose_processor.py --list-models
```

## Architecture

The system is built around a modular architecture with the following components:

### Core Components

1. **`PoseEstimatorBase`** - Abstract base class defining the interface
2. **`PoseEstimatorFactory`** - Factory for creating model instances
3. **`VideoPoseProcessor`** - Main video processing pipeline
4. **Model Implementations** - Specific pose estimation models

### Directory Structure

```
├── pose_estimator_base.py      # Base abstract class
├── model_factory.py            # Factory for model creation
├── video_pose_processor.py     # Main processing script
├── models/
│   ├── __init__.py
│   ├── mediapipe_estimator.py  # MediaPipe implementation
│   └── dummy_estimator.py      # Example dummy implementation
└── requirements.txt
```

## Available Models

### MediaPipe Pose
- **Name**: `mediapipe` or `mp`
- **Description**: Google's MediaPipe Pose solution
- **Keypoints**: 33 landmarks including face, body, and hands
- **Performance**: Real-time capable
- **Accuracy**: Good for most applications

### Dummy Model (for testing)
- **Name**: `dummy` or `test`
- **Description**: Generates random keypoints for testing
- **Keypoints**: 17 COCO-style landmarks
- **Performance**: Very fast
- **Use case**: Testing and development

## Command Line Options

```bash
python video_pose_processor.py [VIDEO_PATH] [OPTIONS]
```

### Required Arguments
- `VIDEO_PATH`: Path to the input video file

### Model Selection
- `--model MODEL`: Pose estimation model to use (default: mediapipe)
- `--list-models`: List available models and exit

### Output Options
- `--output-dir DIR`: Output directory for results (default: pose_output)
- `--no-video`: Skip saving annotated video
- `--no-keypoints`: Skip saving keypoints JSON

### MediaPipe Specific Options
- `--model-complexity {0,1,2}`: Model complexity (0=fast, 1=balanced, 2=accurate)
- `--min-detection-confidence FLOAT`: Minimum detection confidence (0.0-1.0)
- `--min-tracking-confidence FLOAT`: Minimum tracking confidence (0.0-1.0)

## Output Files

The system generates the following output files:

### 1. Annotated Video
- **Filename**: `annotated_[original_name].mp4`
- **Content**: Original video with pose keypoints and skeleton overlay
- **Format**: MP4 video file

### 2. Keypoints Data
- **Filename**: `keypoints_[original_name].json`
- **Content**: Detailed pose data for each frame
- **Format**: JSON file with the following structure:

```json
{
  "video_info": {
    "path": "path/to/video.mp4",
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "total_frames": 300
  },
  "model_info": {
    "name": "MediaPipePoseEstimator",
    "keypoints": ["nose", "left_eye", ...],
    "num_keypoints": 33
  },
  "processing_stats": {
    "total_frames": 300,
    "frames_with_pose": 285,
    "pose_detection_rate": 0.95,
    "avg_fps": 25.5
  },
  "frames": [
    {
      "frame_number": 0,
      "timestamp": 0.0,
      "pose_detected": true,
      "processing_time": 0.04,
      "pose_data": {
        "keypoints": [
          {
            "id": 0,
            "name": "nose",
            "x": 0.5,
            "y": 0.3,
            "confidence": 0.9,
            "pixel_x": 960,
            "pixel_y": 324
          },
          ...
        ],
        "bbox": {
          "x": 100,
          "y": 50,
          "width": 200,
          "height": 400
        },
        "metadata": {
          "model_name": "MediaPipePoseEstimator",
          "processing_time": 0.04
        }
      }
    },
    ...
  ]
}
```

## Adding New Models

The system is designed to be easily extensible. Here's how to add a new pose estimation model:

### Step 1: Create Model Implementation

Create a new file in the `models/` directory:

```python
# models/your_model.py
from pose_estimator_base import PoseEstimatorBase
import numpy as np
from typing import Dict, List, Tuple, Optional, Any

class YourPoseEstimator(PoseEstimatorBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Your initialization code
    
    def initialize(self) -> bool:
        # Initialize your model
        self.is_initialized = True
        return True
    
    def detect_pose(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        # Your pose detection logic
        # Return pose data in the expected format
        pass
    
    def draw_pose(self, frame: np.ndarray, pose_data: Dict[str, Any]) -> np.ndarray:
        # Your visualization logic
        pass
    
    def get_keypoint_names(self) -> List[str]:
        # Return list of keypoint names
        pass
    
    def get_connections(self) -> List[Tuple[int, int]]:
        # Return list of skeleton connections
        pass
```

### Step 2: Register the Model

Add your model to the factory in `model_factory.py`:

```python
from models.your_model import YourPoseEstimator

# Add to the _models dictionary
_models = {
    # ... existing models
    'your_model': YourPoseEstimator,
}
```

### Step 3: Use Your Model

```bash
python video_pose_processor.py video.mp4 --model your_model
```

## Programmatic Usage

You can also use the system programmatically:

```python
from video_pose_processor import VideoPoseProcessor

# Create processor with specific model
processor = VideoPoseProcessor(
    model_name="mediapipe",
    output_dir="my_results",
    model_complexity=2
)

# Process video
results = processor.process_video("path/to/video.mp4")

# Access results
print(f"Processed {results['statistics']['total_frames']} frames")
print(f"Detection rate: {results['statistics']['pose_detection_rate']:.2%}")
```

## Model Interface Requirements

All pose estimation models must implement the `PoseEstimatorBase` interface:

### Required Methods

1. **`initialize()`**: Initialize the model and return success status
2. **`detect_pose(frame)`**: Detect pose in a frame and return keypoint data
3. **`draw_pose(frame, pose_data)`**: Draw pose visualization on frame
4. **`get_keypoint_names()`**: Return list of keypoint names
5. **`get_connections()`**: Return skeleton connections for drawing

### Expected Data Format

The `detect_pose` method should return data in this format:

```python
{
    "keypoints": [
        {
            "id": int,
            "name": str,
            "x": float,      # normalized coordinates (0-1)
            "y": float,
            "confidence": float,  # 0-1
            "pixel_x": int,  # pixel coordinates
            "pixel_y": int
        },
        ...
    ],
    "bbox": {  # optional
        "x": int,
        "y": int,
        "width": int,
        "height": int
    },
    "metadata": {  # optional
        "model_name": str,
        "processing_time": float,
        ...
    }
}
```

## Performance Tips

1. **Model Selection**: Choose the right model for your use case
   - MediaPipe: Good balance of speed and accuracy
   - Custom models: Optimize for specific requirements

2. **Model Complexity**: Adjust based on needs
   - Complexity 0: Fastest, lower accuracy
   - Complexity 1: Balanced (recommended)
   - Complexity 2: Highest accuracy, slower

3. **Video Processing**: For large videos, consider
   - Processing in chunks
   - Using faster model settings
   - Skipping frames if real-time processing isn't needed

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Video Format**: Make sure video format is supported by OpenCV
3. **Memory Issues**: Try processing shorter videos or reducing model complexity
4. **No Pose Detected**: Check video quality and lighting conditions

### Debug Mode

Enable debug logging by modifying the logging level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

### Process Tennis Serve Analysis
```bash
python video_pose_processor.py tennis_serve.mp4 \
    --model mediapipe \
    --model-complexity 2 \
    --output-dir tennis_analysis
```

### Quick Testing with Dummy Model
```bash
python video_pose_processor.py test_video.mp4 \
    --model dummy \
    --output-dir test_output
```

### Batch Processing
```bash
for video in *.mp4; do
    python video_pose_processor.py "$video" --output-dir "results/$(basename "$video" .mp4)"
done
```

## Contributing

To contribute new models or improvements:

1. Follow the `PoseEstimatorBase` interface
2. Add comprehensive tests
3. Update documentation
4. Ensure backward compatibility

## License

This project is open source. Please check individual model licenses for specific requirements. 