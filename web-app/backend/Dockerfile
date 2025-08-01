FROM python:3.11-slim

# Install system dependencies for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgoogle-glog0v5 \
    libgflags2.2 \
    libprotobuf23 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main project files
COPY ../requirements.txt ./main_requirements.txt
RUN pip install --no-cache-dir -r main_requirements.txt

# Copy application code
COPY . .
COPY ../models ./models
COPY ../analyzers ./analyzers
COPY ../video_analysis_pipeline.py .
COPY ../video_analyzer_base.py .
COPY ../video_analyzer_factory.py .
COPY ../pose_estimator_base.py .
COPY ../model_factory.py .

# Create necessary directories
RUN mkdir -p uploads results temp frames frames/roger

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]