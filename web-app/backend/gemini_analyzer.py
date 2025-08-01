#!/usr/bin/env python3
"""
Gemini 2.5 Pro implementation of the VideoAnalyzerBase
Uses Google's Generative AI API for video understanding
"""

import time
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    raise ImportError("Please install google-generativeai: pip install google-generativeai")

from video_analyzer_base import VideoAnalyzerBase

logger = logging.getLogger(__name__)


class GeminiVideoAnalyzer(VideoAnalyzerBase):
    """Gemini 2.5 Pro video analyzer implementation"""
    
    def __init__(self, 
                 api_key: str,
                 model_name: str = "gemini-2.0-flash-exp",
                 temperature: float = 0.1,
                 max_output_tokens: int = 8192,
                 **kwargs):
        """
        Initialize Gemini video analyzer
        
        Args:
            api_key: Google AI Studio API key
            model_name: Gemini model name to use
            temperature: Response randomness (0.0-1.0)
            max_output_tokens: Maximum response length
        """
        super().__init__(api_key, **kwargs)
        
        self.gemini_model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        
        self.client = None
        self.model = None
        self.uploaded_files = {}  # Track uploaded files for cleanup
        
        # Safety settings - adjust as needed
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
    
    def initialize(self) -> bool:
        """Initialize Gemini API client"""
        try:
            # Configure the API key
            genai.configure(api_key=self.api_key)
            
            # Create the model
            self.model = genai.GenerativeModel(
                model_name=self.gemini_model_name,
                safety_settings=self.safety_settings
            )
            
            # Test the connection
            test_response = self.model.generate_content("Test connection")
            if test_response:
                self.is_initialized = True
                logger.info(f"Gemini {self.gemini_model_name} initialized successfully")
                return True
            else:
                logger.error("Failed to get test response from Gemini")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            return False
    
    def upload_video(self, video_path: str) -> Optional[str]:
        """Upload video to Gemini"""
        if not self.is_initialized:
            logger.error("Gemini analyzer not initialized")
            return None
        
        if not self.validate_video_file(video_path):
            logger.error(f"Invalid video file: {video_path}")
            return None
        
        try:
            logger.info(f"Uploading video to Gemini: {video_path}")
            
            # Upload the file
            uploaded_file = genai.upload_file(
                path=video_path,
                display_name=Path(video_path).name
            )
            
            # Wait for processing to complete
            while uploaded_file.state.name == "PROCESSING":
                logger.info("Video processing in progress...")
                time.sleep(2)
                uploaded_file = genai.get_file(uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                logger.error("Video processing failed")
                return None
            
            # Store reference for cleanup
            file_id = uploaded_file.name
            self.uploaded_files[file_id] = uploaded_file
            
            logger.info(f"Video uploaded successfully: {file_id}")
            return file_id
            
        except Exception as e:
            logger.error(f"Failed to upload video: {e}")
            return None
    
    def analyze_video(self, 
                     video_ref: str, 
                     prompt: str, 
                     additional_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Analyze video with Gemini"""
        if not self.is_initialized:
            logger.error("Gemini analyzer not initialized")
            return None
        
        if video_ref not in self.uploaded_files:
            logger.error(f"Video reference not found: {video_ref}")
            return None
        
        try:
            start_time = time.time()
            
            # Prepare the content for analysis
            content_parts = [prompt]
            
            # Add the video
            uploaded_file = self.uploaded_files[video_ref]
            content_parts.append(uploaded_file)
            
            # Add additional data as context if provided
            if additional_data:
                context_text = self._format_additional_data(additional_data)
                if context_text:
                    content_parts.insert(-1, context_text)  # Insert before video
            
            logger.info("Sending video for analysis...")
            
            # Generate analysis
            response = self.model.generate_content(
                content_parts,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_output_tokens,
                )
            )
            
            processing_time = time.time() - start_time
            
            if not response or not response.text:
                logger.error("No response received from Gemini")
                return None
            
            # Prepare result
            result = {
                "analysis": response.text,
                "metadata": {
                    "model_name": self.gemini_model_name,
                    "processing_time": processing_time,
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_output_tokens
                }
            }
            
            # Add usage metadata if available
            if hasattr(response, 'usage_metadata'):
                result["metadata"].update({
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', None),
                    "response_tokens": getattr(response.usage_metadata, 'candidates_token_count', None),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', None)
                })
            
            logger.info(f"Analysis completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze video: {e}")
            return None
    
    def cleanup_video(self, video_ref: str) -> bool:
        """Clean up uploaded video from Gemini"""
        if video_ref not in self.uploaded_files:
            return True  # Already cleaned up or never existed
        
        try:
            uploaded_file = self.uploaded_files[video_ref]
            genai.delete_file(uploaded_file.name)
            del self.uploaded_files[video_ref]
            logger.info(f"Video cleaned up: {video_ref}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup video {video_ref}: {e}")
            return False
    
    def cleanup_all_videos(self):
        """Clean up all uploaded videos"""
        video_refs = list(self.uploaded_files.keys())
        for video_ref in video_refs:
            self.cleanup_video(video_ref)
    
    def _format_additional_data(self, additional_data: Dict[str, Any]) -> Optional[str]:
        """Format additional data as context text"""
        if not additional_data:
            return None
        
        context_parts = []
        
        # Handle keypoints data
        if "keypoints" in additional_data:
            keypoints_data = additional_data["keypoints"]
            context_parts.append("POSE KEYPOINTS DATA:")
            
            # Add summary statistics
            if "processing_stats" in keypoints_data:
                stats = keypoints_data["processing_stats"]
                context_parts.append(f"- Total frames: {stats.get('total_frames', 'N/A')}")
                context_parts.append(f"- Frames with pose: {stats.get('frames_with_pose', 'N/A')}")
                context_parts.append(f"- Detection rate: {stats.get('pose_detection_rate', 0)*100:.1f}%")
            
            # Add model info
            if "model_info" in keypoints_data:
                model_info = keypoints_data["model_info"]
                context_parts.append(f"- Pose model: {model_info.get('name', 'N/A')}")
                context_parts.append(f"- Keypoints: {model_info.get('num_keypoints', 'N/A')}")
            
            # Add sample frame data (first frame with pose)
            if "frames" in keypoints_data:
                frames = keypoints_data["frames"]
                sample_frame = None
                for frame in frames[:10]:  # Check first 10 frames
                    if frame.get("pose_detected"):
                        sample_frame = frame
                        break
                
                if sample_frame:
                    context_parts.append(f"- Sample frame {sample_frame['frame_number']} keypoints:")
                    if "pose_data" in sample_frame and "keypoints" in sample_frame["pose_data"]:
                        keypoints = sample_frame["pose_data"]["keypoints"]
                        for kp in keypoints[:5]:  # Show first 5 keypoints
                            context_parts.append(f"  * {kp['name']}: ({kp['x']:.3f}, {kp['y']:.3f}) conf={kp['confidence']:.3f}")
                        if len(keypoints) > 5:
                            context_parts.append(f"  * ... and {len(keypoints)-5} more keypoints")
        
        # Handle other custom data
        for key, value in additional_data.items():
            if key != "keypoints":
                context_parts.append(f"{key.upper()}: {str(value)[:200]}")  # Limit length
        
        return "\n".join(context_parts) if context_parts else None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Gemini model information"""
        base_info = super().get_model_info()
        base_info.update({
            "gemini_model": self.gemini_model_name,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "uploaded_videos": len(self.uploaded_files)
        })
        return base_info
    
    def cleanup(self):
        """Clean up all resources"""
        self.cleanup_all_videos()
        super().cleanup() 