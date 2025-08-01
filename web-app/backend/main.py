#!/usr/bin/env python3
"""
FastAPI backend for Video Analysis Pipeline
Provides REST API endpoints for video analysis using the existing pipeline
"""

import os
import sys
import json
import uuid
import asyncio
import shutil
import cv2
import re
import base64
import copy
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import logging


# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from video_analysis_pipeline import VideoAnalysisPipeline, create_tennis_serve_prompt, create_general_sports_prompt

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Video Analysis API",
    description="API for analyzing sports videos with pose estimation and AI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results")
TEMP_DIR = Path("temp")
FRAMES_DIR = Path("frames")  # New directory for extracted frames
ROGER_FRAMES_DIR = Path("frames/roger")  # Professional serve frames directory
SLOW_FACTOR = 2.0  # How much to slow down video (2.0 = half speed)

# Create directories
for dir_path in [UPLOAD_DIR, RESULTS_DIR, TEMP_DIR, FRAMES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/results", StaticFiles(directory=str(RESULTS_DIR)), name="results")
app.mount("/frames", StaticFiles(directory=str(FRAMES_DIR)), name="frames")  # Mount frames directory

# In-memory storage for analysis jobs (in production, use Redis or database)
analysis_jobs: Dict[str, Dict[str, Any]] = {}

# Pydantic models
class AnalysisRequest(BaseModel):
    prompt_type: str = Field(..., description="Type of analysis prompt", enum=["tennis", "general", "custom"])
    custom_prompt: Optional[str] = Field(None, description="Custom prompt if prompt_type is 'custom'")
    analyzer: str = Field("gemini", description="Video analyzer to use")
    model: str = Field("gemini-2.0-flash-exp", description="Specific model name")
    temperature: float = Field(0.1, ge=0.0, le=1.0, description="Response randomness")
    max_tokens: int = Field(8192, ge=1, le=32768, description="Maximum response length")

class AnalysisResponse(BaseModel):
    success: bool
    message: str
    analysis_result: Optional[Dict[str, Any]] = None
    extracted_frames: Optional[Dict[str, str]] = None  # phase_name -> frame_url
    professional_frames: Optional[Dict[str, str]] = None  # phase_name -> professional_frame_url
    error: Optional[str] = None

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

# Helper functions
def timestamp_to_seconds(timestamp: str) -> float:
    """
    Convert timestamp in format "M:SS" or "MM:SS" to seconds
    
    Args:
        timestamp: Timestamp string like "0:04", "1:23", etc.
        
    Returns:
        Float seconds
    """
    try:
        # Handle different timestamp formats
        if ':' in timestamp:
            parts = timestamp.split(':')
            if len(parts) == 2:
                minutes, seconds = parts
                return float(minutes) * 60 + float(seconds)
            elif len(parts) == 3:
                hours, minutes, seconds = parts
                return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        else:
            # Assume it's just seconds
            return float(timestamp)
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing timestamp '{timestamp}': {e}")
        return 0.0


def extract_frame_at_timestamp(video_path: str, timestamp_seconds: float, output_path: str) -> bool:
    """
    Extract a single frame from video at specified timestamp
    
    Args:
        video_path: Path to the video file
        timestamp_seconds: Time in seconds to extract frame
        output_path: Path to save the extracted frame
        
    Returns:
        True if successful, False otherwise
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return False
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        # Calculate frame number
        frame_number = int(timestamp_seconds * fps)
        
        # Ensure frame number is within bounds
        if frame_number >= total_frames:
            logger.warning(f"Timestamp {timestamp_seconds}s exceeds video duration {duration}s, using last frame")
            frame_number = total_frames - 1
        elif frame_number < 0:
            logger.warning(f"Negative timestamp {timestamp_seconds}s, using first frame")
            frame_number = 0
        
        # Seek to the specific frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        # Read the frame
        ret, frame = cap.read()
        if not ret:
            logger.error(f"Could not read frame at timestamp {timestamp_seconds}s")
            cap.release()
            return False
        
        # Save the frame
        success = cv2.imwrite(output_path, frame)
        cap.release()
        
        if success:
            logger.info(f"Extracted frame at {timestamp_seconds}s to {output_path}")
        else:
            logger.error(f"Failed to save frame to {output_path}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error extracting frame at timestamp {timestamp_seconds}s: {e}")
        return False


def parse_analysis_json_and_extract_frames(analysis_text: str, video_path: str, analysis_id: str) -> Dict[str, str]:
    """
    Parse the JSON analysis result and extract frames for each phase
    
    Args:
        analysis_text: The analysis result text from LLM (should be JSON)
        video_path: Path to the video file
        analysis_id: Unique analysis ID for file naming
        
    Returns:
        Dictionary mapping phase names to frame file URLs
    """
    extracted_frames = {}
    
    try:
        analysis_text_str = analysis_text.replace("```json", "").replace("```", "")
        # Try to parse the analysis text as JSON
        analysis_json = json.loads(analysis_text_str)
        
        # Check if it has the expected structure
        if 'phases' not in analysis_json:
            logger.warning("No 'phases' key found in analysis JSON")
            return extracted_frames
        
        phases = analysis_json['phases']
        frame_dir = FRAMES_DIR / analysis_id
        frame_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract frames for each phase
        for phase_name, phase_data in phases.items():
            if isinstance(phase_data, dict) and 'frame_timestamp' in phase_data:
                timestamp_str = phase_data['frame_timestamp']
                timestamp_seconds = timestamp_to_seconds(timestamp_str)
                
                # Create frame filename
                frame_filename = f"{phase_name}_{timestamp_str.replace(':', '-')}.jpg"
                frame_path = frame_dir / frame_filename
                
                # Extract frame
                if extract_frame_at_timestamp(str(video_path), timestamp_seconds, str(frame_path)):
                    # Create URL for the extracted frame
                    frame_url = f"/frames/{analysis_id}/{frame_filename}"
                    extracted_frames[phase_name] = frame_url
                    logger.info(f"Extracted frame for phase '{phase_name}' at {timestamp_str}")
                else:
                    logger.error(f"Failed to extract frame for phase '{phase_name}' at {timestamp_str}")
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse analysis result as JSON: {e}")
        logger.info("Analysis text might not be valid JSON, skipping frame extraction")
    except Exception as e:
        logger.error(f"Error during frame extraction: {e}")
    
    return extracted_frames


def get_professional_serve_frames(analysis_text: str) -> Dict[str, str]:
    """
    Get professional serve frame URLs for each detected phase
    
    Args:
        analysis_text: The analysis result text from LLM (should be JSON)
        
    Returns:
        Dictionary mapping phase names to professional serve frame URLs
    """
    professional_frames = {}
    
    try:
        analysis_text_str = analysis_text.replace("```json", "").replace("```", "")
        # Try to parse the analysis text as JSON
        analysis_json = json.loads(analysis_text_str)
        
        # Check if it has the expected structure
        if 'phases' not in analysis_json:
            logger.warning("No 'phases' key found in analysis JSON")
            return professional_frames
        
        phases = analysis_json['phases']
        
        # Map each detected phase to professional frame if it exists
        for phase_name in phases.keys():
            # Look for professional frame file that matches the phase name
            for roger_file in ROGER_FRAMES_DIR.glob("*.jpg"):
                if roger_file.stem.startswith(phase_name):
                    professional_frame_url = f"/frames/roger/{roger_file.name}"
                    professional_frames[phase_name] = professional_frame_url
                    logger.info(f"Found professional frame for phase '{phase_name}': {roger_file.name}")
                    break
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse analysis result as JSON for professional frames: {e}")
    except Exception as e:
        logger.error(f"Error getting professional serve frames: {e}")
    
    return professional_frames


def get_video_rotation(video_path: str) -> int:
    """
    Get rotation angle from video metadata
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Rotation angle (0, 90, 180, 270)
    """
    try:
        import subprocess
        import json
        
        # Use ffprobe to get rotation metadata
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_streams', video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            metadata = json.loads(result.stdout)
            for stream in metadata.get('streams', []):
                if stream.get('codec_type') == 'video':
                    # Check for rotation in side_data_list
                    side_data_list = stream.get('side_data_list', [])
                    for side_data in side_data_list:
                        if side_data.get('side_data_type') == 'Display Matrix':
                            rotation = side_data.get('rotation', 0)
                            return int(-rotation)  # Negative because display matrix rotation is opposite
                    
                    # Check for rotation tag
                    tags = stream.get('tags', {})
                    if 'rotate' in tags:
                        return int(tags['rotate'])
        
        return 0
    except Exception as e:
        logger.warning(f"Could not get video rotation: {e}")
        return 0


def rotate_frame(frame, angle: int):
    """
    Rotate frame by given angle
    
    Args:
        frame: Input frame
        angle: Rotation angle (90, 180, 270)
        
    Returns:
        Rotated frame
    """
    if angle == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        return frame


def slow_down_video(input_path: str, output_path: str, slow_factor: float = 2.0) -> bool:
    """
    Slow down video by reducing playback speed (creating slow motion effect)
    Preserves the original video orientation for iPhone .mov files
    
    Args:
        input_path: Path to the input video file
        output_path: Path to save the slowed video
        slow_factor: How much to slow down (2.0 = half speed, 4.0 = quarter speed)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get rotation angle from metadata
        rotation_angle = get_video_rotation(input_path)
        logger.info(f"Detected rotation angle: {rotation_angle} degrees")
        
        # Open input video
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            return False
        
        # Get original video properties
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Adjust dimensions if video needs rotation
        if rotation_angle == 90 or rotation_angle == 270:
            # Swap width and height for 90/270 degree rotations
            output_width, output_height = height, width
        else:
            output_width, output_height = width, height
        
        # Calculate new FPS for slow motion
        new_fps = original_fps / slow_factor
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, new_fps, (output_width, output_height))
        
        # Read and write all frames (no skipping)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Apply rotation if needed
            if rotation_angle != 0:
                frame = rotate_frame(frame, rotation_angle)
            
            # Write the frame (all frames are preserved)
            out.write(frame)
        
        # Release everything
        cap.release()
        out.release()
        
        return True
        
    except Exception as e:
        logger.error(f"Error slowing down video: {e}")
        return False

def get_prompt_by_type(prompt_type: str, custom_prompt: Optional[str] = None) -> str:
    """Get analysis prompt based on type"""
    if prompt_type == "custom":
        if not custom_prompt:
            raise HTTPException(status_code=400, detail="Custom prompt required for custom prompt type")
        return custom_prompt
    elif prompt_type == "tennis":
        return create_tennis_serve_prompt()
    elif prompt_type == "general":
        return create_general_sports_prompt()
    else:
        raise HTTPException(status_code=400, detail="Invalid prompt type")

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Video Analysis API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_video(
    video: UploadFile = File(..., description="Video file to analyze"),
    api_key: str = Form(..., description="API key for the video analysis service"),
    prompt_type: str = Form("tennis", description="Type of analysis prompt"),
    custom_prompt: Optional[str] = Form(None, description="Custom prompt if prompt_type is 'custom'"),
    analyzer: str = Form("gemini", description="Video analyzer to use"),
    model: str = Form("gemini-2.0-flash-exp", description="Specific model name"),
    temperature: float = Form(0.1, description="Response randomness"),
    max_tokens: int = Form(8192, description="Maximum response length")
):
    """
    Analyze a video file and return the analysis result directly
    """
    # Validate file
    if not video.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Check file extension
    allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    file_extension = Path(video.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique ID for this analysis
    analysis_id = str(uuid.uuid4())
    
    # Save uploaded file
    video_path = UPLOAD_DIR / f"{analysis_id}_{video.filename}"
    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")
    
    try:
        # Slow down video before analysis
        processed_video_path = UPLOAD_DIR / f"{analysis_id}_processed_{video.filename}"
        if not slow_down_video(str(video_path), str(processed_video_path), slow_factor=SLOW_FACTOR):
            # If slow down fails, use original video
            logger.warning(f"Failed to slow down video for {video.filename}, using original video")
            processed_video_path = video_path
        else:
            logger.info(f"Successfully slowed down video by {SLOW_FACTOR}x for {video.filename}")
        
        # Get prompt
        prompt = get_prompt_by_type(prompt_type, custom_prompt)
        
        # Create pipeline
        pipeline = VideoAnalysisPipeline(
            analyzer_name=analyzer,
            api_key=api_key,
            output_dir=str(RESULTS_DIR / analysis_id),
            model_name=model,
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        
        # Analyze video with processed (FPS-reduced) video
        result = pipeline.analyze_video(
            video_path=str(processed_video_path),
            prompt=prompt,
            cleanup_after=True
        )

        # Extract frames based on analysis result
        extracted_frames = {}
        professional_frames = {}
        if result and 'analysis' in result and 'analysis' in result['analysis']:
            analysis_text = copy.deepcopy(result['analysis']['analysis'])
            extracted_frames = parse_analysis_json_and_extract_frames(
                analysis_text, 
                str(processed_video_path), 
                analysis_id
            )
            professional_frames = get_professional_serve_frames(analysis_text)
        
        # Cleanup
        pipeline.cleanup()
        
        # # Remove uploaded video files
        # if os.path.exists(video_path):
        #     os.remove(video_path)
        # if os.path.exists(processed_video_path) and processed_video_path != video_path:
        #     os.remove(processed_video_path)
        
        return AnalysisResponse(
            success=True,
            message="Video analysis completed successfully",
            analysis_result=result,
            extracted_frames=extracted_frames if extracted_frames else None,
            professional_frames=professional_frames if professional_frames else None
        )
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(video_path):
            os.remove(video_path)
        if 'processed_video_path' in locals() and os.path.exists(processed_video_path) and processed_video_path != video_path:
            os.remove(processed_video_path)
        
        # Remove results directory if it exists
        results_dir = RESULTS_DIR / analysis_id
        if results_dir.exists():
            shutil.rmtree(results_dir)
        
        # Remove frames directory if it exists
        frames_dir = FRAMES_DIR / analysis_id
        if frames_dir.exists():
            shutil.rmtree(frames_dir)
        
        return AnalysisResponse(
            success=False,
            message="Video analysis failed",
            error=str(e)
        )

@app.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get status of an analysis job"""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = analysis_jobs[job_id]
    return JobStatus(**job)

@app.get("/jobs")
async def list_jobs():
    """List all analysis jobs"""
    return {"jobs": list(analysis_jobs.values())}

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete an analysis job and its files"""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = analysis_jobs[job_id]
    
    # Clean up files
    try:
        # Remove uploaded video
        if "video_path" in job and os.path.exists(job["video_path"]):
            os.remove(job["video_path"])
        
        # Remove results directory
        results_dir = RESULTS_DIR / job_id
        if results_dir.exists():
            shutil.rmtree(results_dir)
        
        # Remove frames directory
        frames_dir = FRAMES_DIR / job_id
        if frames_dir.exists():
            shutil.rmtree(frames_dir)
            
    except Exception as e:
        print(f"Error cleaning up job {job_id}: {e}")
    
    # Remove from memory
    del analysis_jobs[job_id]
    
    return {"message": f"Job {job_id} deleted successfully"}

@app.get("/results/{job_id}")
async def get_results_file(job_id: str):
    """Download results file for a job"""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = analysis_jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    results_dir = RESULTS_DIR / job_id
    json_files = list(results_dir.glob("*.json"))
    
    if not json_files:
        raise HTTPException(status_code=404, detail="Results file not found")
    
    return FileResponse(
        path=json_files[0],
        filename=f"analysis_results_{job_id}.json",
        media_type="application/json"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 