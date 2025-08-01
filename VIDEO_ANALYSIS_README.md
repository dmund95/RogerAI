# Video Analysis Pipeline with AI Models

A modular system for analyzing videos using AI models like Gemini 2.5 Pro, with optional integration of pose estimation data for enhanced sports and movement analysis.

## 🚀 Features

- **Modular Architecture**: Easy to add new video analysis models (OpenAI, Claude, etc.)
- **Gemini Integration**: Built-in support for Google's Gemini 2.5 Pro
- **Pose Data Integration**: Combines pose estimation keypoints with video analysis
- **Tennis-Specific Analysis**: Specialized prompts for tennis serve analysis
- **Batch Processing**: Analyze multiple videos with different prompts
- **Comprehensive Output**: Detailed JSON results with metadata and statistics
- **Automatic Cleanup**: Manages uploaded files and API resources

## 📋 Prerequisites

1. **API Key**: Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Video Files**: Annotated videos from the pose estimation system (or any MP4/AVI videos)
3. **Python 3.8+**: Required for the system to run

## 🛠️ Installation

1. **Install dependencies:**
```bash
pip install -r requirements_video_analysis.txt
```

2. **Set up your API key** (choose one method):
```bash
# Method 1: Environment variable (recommended)
export GEMINI_API_KEY="your-api-key-here"

# Method 2: Pass directly to scripts
python video_analysis_pipeline.py video.mp4 --api_key "your-api-key-here"
```

## 🎯 Quick Start

### Basic Tennis Serve Analysis
```bash
# Analyze a tennis serve video with pose keypoints
python video_analysis_pipeline.py serve_video.mp4 \
    --api_key "your-api-key" \
    --keypoints_json "keypoints_serve_video.json" \
    --prompt_type tennis
```

### Custom Analysis
```bash
# Use a custom prompt for specific analysis
python video_analysis_pipeline.py movement_video.mp4 \
    --api_key "your-api-key" \
    --prompt "Analyze the balance and coordination in this movement" \
    --output_dir custom_analysis
```

### General Sports Analysis
```bash
# General sports movement analysis
python video_analysis_pipeline.py sports_video.mp4 \
    --api_key "your-api-key" \
    --prompt_type general
```

## 📁 System Architecture

```
├── video_analyzer_base.py          # Abstract base class for all analyzers
├── video_analyzer_factory.py       # Factory for creating analyzer instances
├── video_analysis_pipeline.py      # Main pipeline and CLI interface
├── analyzers/
│   ├── __init__.py
│   └── gemini_analyzer.py          # Gemini 2.5 Pro implementation
├── video_analysis_examples.py      # Usage examples
└── requirements_video_analysis.txt # Dependencies
```

## 🔧 Command Line Interface

### Required Arguments
- `video_path`: Path to the input video file

### API Configuration
- `--api_key`: Your Gemini API key (or set GEMINI_API_KEY env var)
- `--analyzer`: Video analyzer to use (default: gemini)
- `--model`: Specific model name (default: gemini-2.0-flash-exp)

### Analysis Options
- `--prompt`: Custom analysis prompt
- `--prompt_type`: Predefined prompt type (tennis, general, custom)
- `--keypoints_json`: Path to pose keypoints JSON file
- `--output_dir`: Output directory for results

### Model Parameters
- `--temperature`: Response creativity (0.0-1.0, default: 0.1)
- `--max_tokens`: Maximum response length (default: 8192)
- `--no_cleanup`: Keep uploaded videos for debugging

## 📊 Output Format

The system generates detailed JSON analysis files:

```json
{
  "video_path": "path/to/video.mp4",
  "analyzer_info": {
    "name": "GeminiVideoAnalyzer",
    "gemini_model": "gemini-2.0-flash-exp",
    "temperature": 0.1,
    "initialized": true
  },
  "prompt": "Analysis prompt used...",
  "analysis": {
    "analysis": "Detailed AI analysis text...",
    "metadata": {
      "model_name": "gemini-2.0-flash-exp",
      "processing_time": 15.3,
      "prompt_tokens": 1250,
      "response_tokens": 890,
      "total_tokens": 2140
    }
  },
  "additional_data_provided": true
}
```

## 🎾 Tennis Serve Analysis

## 🔄 Programmatic Usage

```python
from video_analysis_pipeline import VideoAnalysisPipeline

# Create pipeline
pipeline = VideoAnalysisPipeline(
    analyzer_name="gemini",
    api_key="your-api-key",
    model_name="gemini-2.0-flash-exp",
    temperature=0.1
)

# Analyze video
result = pipeline.analyze_video(
    video_path="serve.mp4",
    prompt="Analyze this tennis serve technique",
    keypoints_json="serve_keypoints.json"
)

print(f"Analysis: {result['analysis']['analysis']}")
pipeline.cleanup()
```

## 📦 Batch Processing

```python
# Configure multiple videos
video_configs = [
    {
        "video_path": "serve1.mp4",
        "prompt": "Analyze serve technique",
        "keypoints_json": "serve1_keypoints.json"
    },
    {
        "video_path": "serve2.mp4", 
        "prompt": "Compare to professional technique",
        "keypoints_json": "serve2_keypoints.json"
    }
]

# Process batch
results = pipeline.batch_analyze(video_configs)
```

## 🔌 Adding New AI Models

The system is designed for easy extensibility:

### 1. Create Analyzer Implementation
```python
# analyzers/your_model_analyzer.py
from video_analyzer_base import VideoAnalyzerBase

class YourModelAnalyzer(VideoAnalyzerBase):
    def initialize(self) -> bool:
        # Initialize your model
        pass
    
    def upload_video(self, video_path: str) -> Optional[str]:
        # Upload video to your service
        pass
    
    def analyze_video(self, video_ref: str, prompt: str, 
                     additional_data: Optional[Dict] = None) -> Optional[Dict]:
        # Analyze with your model
        pass
    
    def cleanup_video(self, video_ref: str) -> bool:
        # Cleanup uploaded video
        pass
```

### 2. Register in Factory
```python
# video_analyzer_factory.py
from analyzers.your_model_analyzer import YourModelAnalyzer

_analyzers = {
    # ... existing analyzers
    'your_model': YourModelAnalyzer,
}
```

### 3. Use Your Model
```bash
python video_analysis_pipeline.py video.mp4 --analyzer your_model --api_key "your-key"
```

## 🎛️ Configuration Options

### Model Selection
- `gemini`: Default Gemini 2.0 Flash
- `gemini-2.5-pro`: Higher accuracy, slower
- `gemini-2.0-flash-exp`: Experimental features

### Temperature Settings
- `0.0-0.2`: Precise, consistent analysis
- `0.3-0.7`: Balanced creativity and accuracy
- `0.8-1.0`: Creative, varied responses

### Token Limits
- `4096`: Quick analysis, lower cost
- `8192`: Detailed analysis (recommended)
- `16384+`: Comprehensive analysis, higher cost

## 📈 Performance Tips

1. **Video Quality**: Higher quality videos yield better analysis
2. **Pose Data**: Including keypoints significantly improves analysis quality
3. **Prompt Engineering**: Specific prompts get better results
4. **Batch Processing**: More efficient for multiple videos
5. **Temperature Tuning**: Lower for technical analysis, higher for creative insights

## 🔍 Troubleshooting

### Common Issues

**API Key Errors**
```bash
# Check if API key is set
echo $GEMINI_API_KEY

# Test API connection
python -c "import google.generativeai as genai; genai.configure(api_key='your-key'); print('API OK')"
```

**Video Upload Failures**
- Check video format (MP4, AVI, MOV supported)
- Ensure file size < 100MB
- Verify internet connection

**Analysis Errors**
- Check prompt length (not too long)
- Verify video content is appropriate
- Try different temperature settings

### Debug Mode
```bash
# Keep uploaded videos for debugging
python video_analysis_pipeline.py video.mp4 --api_key "key" --no_cleanup

# Enable verbose logging
export PYTHONPATH=. && python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
# Your analysis code here
"
```

## 💰 Cost Optimization

1. **Smart Prompts**: Be specific to get better results faster
2. **Batch Processing**: Analyze multiple videos in one session
3. **Temperature**: Lower temperature = more consistent costs
4. **Token Management**: Set appropriate max_tokens limits
5. **Video Length**: Shorter videos cost less to process

## 🔗 Integration with Pose Estimation

This system works seamlessly with the pose estimation pipeline:

```bash
# Step 1: Extract pose keypoints
python video_pose_processor.py serve.mp4 --model mediapipe --output_dir pose_output

# Step 2: Analyze with AI model
python video_analysis_pipeline.py pose_output/annotated_serve.mp4 \
    --keypoints_json pose_output/keypoints_serve.json \
    --prompt_type tennis \
    --api_key "your-key"
```

## 📚 Examples

Run the examples to see different usage patterns:

```bash
# Basic examples (no video files needed)
python video_analysis_examples.py

# Full examples (update paths first)
# Edit video_analysis_examples.py with your video paths and API key
python video_analysis_examples.py
```

## 🤝 Contributing

To add new AI models or improve the system:

1. Follow the `VideoAnalyzerBase` interface
2. Add comprehensive error handling
3. Include usage examples
4. Update documentation
5. Test with various video types

## 📄 License

This project is open source. Check individual AI service terms for API usage requirements.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the examples
3. Ensure all dependencies are installed
4. Verify API key permissions 