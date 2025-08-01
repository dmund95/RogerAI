#!/usr/bin/env python3
"""
Video Analysis Pipeline
Combines pose estimation with video understanding models for comprehensive analysis
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Optional, Any

from video_analyzer_factory import VideoAnalyzerFactory
from video_analyzer_base import VideoAnalyzerBase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VideoAnalysisPipeline:
    """Main pipeline for video analysis with pose data integration"""
    
    def __init__(self, 
                 analyzer_name: str,
                 api_key: str,
                 output_dir: str = "analysis_output",
                 **analyzer_kwargs):
        """
        Initialize the video analysis pipeline
        
        Args:
            analyzer_name: Name of the video analyzer to use
            api_key: API key for the video analysis service
            output_dir: Directory to save analysis results
            **analyzer_kwargs: Additional arguments for the analyzer
        """
        self.analyzer_name = analyzer_name
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.analyzer_kwargs = analyzer_kwargs
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize analyzer
        self.analyzer = VideoAnalyzerFactory.create_analyzer(
            analyzer_name, api_key, **analyzer_kwargs
        )
        
        if not self.analyzer:
            raise ValueError(f"Failed to create analyzer: {analyzer_name}")
        
        # Track uploaded videos for cleanup
        self.uploaded_videos = []
    
    def analyze_video(self, 
                     video_path: str,
                     prompt: str,
                     keypoints_json: Optional[str] = None,
                     custom_data: Optional[Dict[str, Any]] = None,
                     cleanup_after: bool = True) -> Dict[str, Any]:
        """
        Analyze a video with the given prompt
        
        Args:
            video_path: Path to the video file
            prompt: Analysis prompt/instructions
            keypoints_json: Optional path to keypoints JSON file
            custom_data: Optional custom additional data
            cleanup_after: Whether to cleanup uploaded video after analysis
            
        Returns:
            Dictionary containing analysis results
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        logger.info(f"Starting video analysis: {video_path}")
        logger.info(f"Using analyzer: {self.analyzer.model_name}")
        
        try:
            # Initialize analyzer
            if not self.analyzer.initialize():
                raise RuntimeError("Failed to initialize video analyzer")
            
            # Upload video
            logger.info("Uploading video...")
            video_ref = self.analyzer.upload_video(video_path)
            if not video_ref:
                raise RuntimeError("Failed to upload video")
            
            self.uploaded_videos.append(video_ref)
            
            additional_data = None

            # Analyze video
            logger.info("Analyzing video...")
            analysis_result = self.analyzer.analyze_video(
                video_ref, prompt, additional_data
            )
            
            if not analysis_result:
                raise RuntimeError("Failed to analyze video")
            
            # Prepare final result
            result = {
                "video_path": video_path,
                "analyzer_info": self.analyzer.get_model_info(),
                "prompt": prompt,
                "analysis": analysis_result,
                "additional_data_provided": additional_data is not None and len(additional_data) > 0
            }
            
            # Save analysis result
            self._save_analysis_result(video_path, result)
            
            # Cleanup if requested
            if cleanup_after:
                self.analyzer.cleanup_video(video_ref)
                if video_ref in self.uploaded_videos:
                    self.uploaded_videos.remove(video_ref)
            
            logger.info("Video analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error during video analysis: {e}")
            raise
    
    def batch_analyze(self, 
                     video_configs: list,
                     cleanup_after_each: bool = True) -> Dict[str, Any]:
        """
        Analyze multiple videos with different prompts
        
        Args:
            video_configs: List of dictionaries with video analysis configurations
                Each dict should contain: video_path, prompt, keypoints_json (optional)
            cleanup_after_each: Whether to cleanup each video after analysis
            
        Returns:
            Dictionary containing all analysis results
        """
        results = {}
        
        for i, config in enumerate(video_configs):
            video_path = config['video_path']
            prompt = config['prompt']
            keypoints_json = config.get('keypoints_json')
            custom_data = config.get('custom_data')
            
            logger.info(f"Processing video {i+1}/{len(video_configs)}: {Path(video_path).name}")
            
            try:
                result = self.analyze_video(
                    video_path=video_path,
                    prompt=prompt,
                    keypoints_json=keypoints_json,
                    custom_data=custom_data,
                    cleanup_after=cleanup_after_each
                )
                results[Path(video_path).stem] = result
                
            except Exception as e:
                logger.error(f"Failed to analyze {video_path}: {e}")
                results[Path(video_path).stem] = {"error": str(e)}
        
        # Save batch results
        batch_result_file = self.output_dir / "batch_analysis_results.json"
        try:
            with open(batch_result_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Batch results saved to: {batch_result_file}")
        except Exception as e:
            logger.error(f"Failed to save batch results: {e}")
        
        return results
    
    def _save_analysis_result(self, video_path: str, result: Dict[str, Any]):
        """Save analysis result to JSON file"""
        video_name = Path(video_path).stem
        result_file = self.output_dir / f"analysis_{video_name}.json"
        
        try:
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"Analysis result saved to: {result_file}")
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
    
    def cleanup_all_videos(self):
        """Clean up all uploaded videos"""
        for video_ref in self.uploaded_videos[:]:  # Copy list to avoid modification during iteration
            self.analyzer.cleanup_video(video_ref)
            self.uploaded_videos.remove(video_ref)
    
    def cleanup(self):
        """Clean up all resources"""
        self.cleanup_all_videos()
        if self.analyzer:
            self.analyzer.cleanup()


def create_tennis_serve_prompt() -> str:
    """Create a comprehensive tennis serve analysis prompt with structured JSON output"""
    return """
You are an expert tennis biomechanics coach. Your task is to analyze the provided tennis serve video with pose keypoints overlay. Evaluate the serve by breaking it down into five distinct phases.

For each phase, analyze the critical biomechanical markers and provide:
- Frame timestamp for the exact frame you are analyzing
- Score from 1 to 10 (1 being poor, 10 being perfect)
- Concise, actionable feedback (maximum 20 words)
- Key observations about technique

**PHASE ANALYSIS CRITERIA:**

PHASE 1: Preparation & Stance
Focus: A balanced and athletic starting position.

PHASE 2: Loading & Toss
Focus: Evaluate the "leg drive" and body tilt. Look for a front knee flexion angle greater than 15 degrees. Observe the lateral rearward tilt of the shoulders and pelvis to prepare for trunk rotation. The toss should be consistent and placed correctly.

PHASE 3: Cocking Phase (Trophy Pose)
Focus: Assess the shoulder and arm position at the peak of the backswing. The upper arm should be positioned slightly anterior to (in front of) the plane of the body, not directly out to the side or behind.

PHASE 4: Acceleration & Impact
Focus: Look for a powerful and rapid sequence of movements. This includes a vigorous knee extension driving upwards, a quick reversal of trunk rotation (from hyperextension to flexion), and rapid internal rotation of the shoulder as the racquet accelerates towards the ball.

PHASE 5: Follow-Through
Focus: Analyze the deceleration of the arm and body. The motion should be fluid and complete, with the arm crossing the body to safely dissipate energy and prevent injury.

**IMPORTANT: You must respond with ONLY valid JSON in the exact format specified below. Do not include any text before or after the JSON.**
**REQUIRED JSON OUTPUT FORMAT:**

{
  "analysis_type": "tennis_serve_biomechanics",
  "overall_score": 0,
  "phases": {
    "preparation_stance": {
      "frame_timestamp": "0:04",
      "score": 0,
      "feedback": "Brief actionable feedback under 20 words",
      "observations": ["Key observation 1", "Key observation 2"]
    },
    "loading_toss": {
      "frame_timestamp": "0:00",
      "score": 0,
      "feedback": "Brief actionable feedback under 20 words",
      "observations": ["Key observation 1", "Key observation 2"]
    },
    "cocking_trophy": {
      "frame_timestamp": "0:00",
      "score": 0,
      "feedback": "Brief actionable feedback under 20 words",
      "observations": ["Key observation 1", "Key observation 2"]
    },
    "acceleration_impact": {
      "frame_timestamp": "0:00",
      "score": 0,
      "feedback": "Brief actionable feedback under 20 words",
      "observations": ["Key observation 1", "Key observation 2"]
    },
    "follow_through": {
      "frame_timestamp": "0:00",
      "score": 0,
      "feedback": "Brief actionable feedback under 20 words",
      "observations": ["Key observation 1", "Key observation 2"]
    }
  },
  "recommendations": {
    "improvement_areas": ["Area 1", "Area 2", "Area 3"],
    "technical_adjustments": ["Adjustment 1", "Adjustment 2"],
    "training_focus": ["Focus area 1", "Focus area 2"],
    "comparison_to_pro": "Brief comparison to professional technique standards"
  },
  "biomechanical_summary": {
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "injury_risk_factors": ["Risk factor 1", "Risk factor 2"],
    "efficiency_rating": 0
  }
}

Base your analysis on the pose keypoints data and visual analysis of the serve motion. Ensure all scores are integers between 1-10, and the overall_score is the average of all phase scores.
"""

# **SERVE TECHNIQUE ANALYSIS:**
# 1. **Preparation Phase:**
#    - Stance and positioning
#    - Ball and racket grip
#    - Initial body alignment

# 2. **Ball Toss:**
#    - Toss height and placement
#    - Consistency and timing
#    - Coordination with racket preparation

# 3. **Loading Phase:**
#    - Shoulder turn and coiling
#    - Weight transfer
#    - Kinetic chain setup

# 4. **Acceleration Phase:**
#    - Hip and shoulder rotation sequence
#    - Racket head acceleration
#    - Power generation mechanics

# 5. **Contact Point:**
#    - Contact height and position
#    - Body extension
#    - Racket face angle

# 6. **Follow-through:**
#    - Completion of swing
#    - Body balance and recovery
#    - Deceleration mechanics

# **BIOMECHANICAL ASSESSMENT:**
# - Joint coordination and timing
# - Energy transfer efficiency
# - Balance and stability throughout motion
# - Potential injury risk factors

# **PERFORMANCE METRICS:**
# - Estimate serve speed potential
# - Power generation assessment
# - Consistency indicators
# - Technical efficiency rating

# **RECOMMENDATIONS:**
# - Specific areas for improvement
# - Technical adjustments needed
# - Training focus areas
# - Comparison to professional technique standards


def create_general_sports_prompt() -> str:
    """Create a general sports movement analysis prompt"""
    return """
Analyze this sports video with pose keypoints data. Please provide:

**MOVEMENT ANALYSIS:**
- Identify the sport and specific movement/technique being performed
- Break down the movement into key phases
- Assess technique quality and efficiency

**BIOMECHANICAL INSIGHTS:**
- Joint coordination and sequencing
- Power generation and energy transfer
- Balance and stability analysis
- Movement efficiency assessment

**TECHNICAL FEEDBACK:**
- Strengths in the technique
- Areas needing improvement
- Specific technical corrections
- Training recommendations

**PERFORMANCE INDICATORS:**
- Movement quality rating
- Consistency assessment
- Injury risk factors
- Comparison to optimal technique

Use the pose keypoints data to provide specific, actionable feedback on the athletic performance shown in the video.
"""


def main():
    """Main function for command line interface"""
    parser = argparse.ArgumentParser(description="Video Analysis Pipeline with Pose Data Integration")
    
    # Required arguments
    parser.add_argument("video_path", help="Path to input video file")
    parser.add_argument("--api_key", required=True, help="API key for the video analysis service")
    
    # Analyzer selection
    parser.add_argument("--analyzer", default="gemini", 
                       help="Video analyzer to use (default: gemini)")
    parser.add_argument("--model", default="gemini-2.0-flash-exp",
                       help="Specific model name (default: gemini-2.0-flash-exp)")
    
    # Analysis options
    parser.add_argument("--prompt", help="Custom analysis prompt")
    parser.add_argument("--prompt_type", choices=["tennis", "general", "custom"], default="tennis",
                       help="Type of analysis prompt to use")
    parser.add_argument("--keypoints_json", help="Path to keypoints JSON file")
    
    # Output options
    parser.add_argument("--output_dir", default="analysis_output",
                       help="Output directory for results")
    parser.add_argument("--no_cleanup", action="store_true",
                       help="Don't cleanup uploaded videos (for debugging)")
    
    # Model parameters
    parser.add_argument("--temperature", type=float, default=0.1,
                       help="Response randomness (0.0-1.0)")
    parser.add_argument("--max_tokens", type=int, default=8192,
                       help="Maximum response length")
    
    args = parser.parse_args()
    
    # Validate video file
    if not os.path.exists(args.video_path):
        logger.error(f"Video file not found: {args.video_path}")
        sys.exit(1)
    
    # Determine prompt
    if args.prompt:
        prompt = args.prompt
    elif args.prompt_type == "tennis":
        prompt = create_tennis_serve_prompt()
    elif args.prompt_type == "general":
        prompt = create_general_sports_prompt()
    else:
        logger.error("Custom prompt type requires --prompt argument")
        sys.exit(1)
    
    try:
        # Create pipeline
        pipeline = VideoAnalysisPipeline(
            analyzer_name=args.analyzer,
            api_key=args.api_key,
            output_dir=args.output_dir,
            model_name=args.model,
            temperature=args.temperature,
            max_output_tokens=args.max_tokens
        )
        
        # Analyze video
        result = pipeline.analyze_video(
            video_path=args.video_path,
            prompt=prompt,
            keypoints_json=args.keypoints_json,
            cleanup_after=not args.no_cleanup
        )
        
        # Print summary
        print("\n" + "="*80)
        print("VIDEO ANALYSIS COMPLETE")
        print("="*80)
        print(f"Video: {result['video_path']}")
        print(f"Analyzer: {result['analyzer_info']['name']}")
        print(f"Model: {result['analyzer_info'].get('gemini_model', 'N/A')}")
        print(f"Processing time: {result['analysis']['metadata']['processing_time']:.2f}s")
        if 'total_tokens' in result['analysis']['metadata']:
            print(f"Tokens used: {result['analysis']['metadata']['total_tokens']}")
        print(f"Output directory: {args.output_dir}")
        print("\n" + "="*80)
        print("ANALYSIS RESULT:")
        print("="*80)
        print(result['analysis']['analysis'])
        print("="*80)
        
        # Cleanup
        if not args.no_cleanup:
            pipeline.cleanup()
        
    except Exception as e:
        logger.error(f"Error in video analysis pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 