# Video Analysis Web Application

A modern web application for AI-powered sports video analysis using React frontend and FastAPI backend.

## Features

- **Video Upload**: Drag & drop interface for uploading sports videos
- **AI Analysis**: Powered by Google's Gemini AI models
- **Real-time Progress**: Live updates on analysis progress
- **Multiple Analysis Types**: Tennis serve analysis, general sports analysis, or custom prompts
- **Results Viewer**: Beautiful interface to view and download analysis results
- **Job Management**: Track all your analysis jobs with status monitoring

## Architecture

- **Frontend**: React with Tailwind CSS for modern UI
- **Backend**: FastAPI with async processing
- **AI Integration**: Google Gemini API for video analysis
- **File Handling**: Secure video upload and processing

## Prerequisites

- Python 3.11+ (for the existing video analysis pipeline)
- Node.js 16+ and npm (for React frontend)
- Google Gemini API key

## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend directory
cd web-app/backend

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python main.py
```

The backend will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd web-app/frontend

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

The frontend will be available at `http://localhost:3000`

### 3. Get API Key

1. Go to [Google AI Studio](https://ai.google.dev/)
2. Create a new API key
3. Use this key in the web application

## Usage

1. **Upload Video**: Go to the "Analyze" page and upload your sports video
2. **Configure Analysis**: Enter your API key and choose analysis type
3. **Monitor Progress**: Track the analysis progress on the "Jobs" page
4. **View Results**: Once complete, view detailed analysis results

## API Endpoints

### Backend API (`http://localhost:8000`)

- `GET /` - API information
- `GET /health` - Health check
- `POST /analyze` - Upload and analyze video
- `GET /jobs` - List all analysis jobs
- `GET /jobs/{job_id}` - Get specific job status
- `DELETE /jobs/{job_id}` - Delete a job
- `GET /results/{job_id}` - Download results file

### Example API Usage

```bash
# Upload video for analysis
curl -X POST "http://localhost:8000/analyze" \
  -F "video=@your_video.mp4" \
  -F "api_key=your_gemini_api_key" \
  -F "prompt_type=tennis"

# Check job status
curl "http://localhost:8000/jobs/{job_id}"
```

## Configuration

### Backend Configuration

The backend can be configured through environment variables:

- `UPLOAD_DIR`: Directory for uploaded videos (default: `uploads`)
- `RESULTS_DIR`: Directory for analysis results (default: `results`)

### Frontend Configuration

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

### Custom Analysis
Use your own prompts for specialized analysis requirements.

## Development

### Backend Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## Deployment

### Backend Deployment

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables
3. Run with: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Frontend Deployment

1. Build the app: `npm run build`
2. Serve the `build` directory with a web server
3. Configure API URL in environment variables

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure the backend is running on `http://localhost:8000`
2. **API Key Issues**: Verify your Gemini API key is valid
3. **Video Upload Failures**: Check file format and size limits
4. **Analysis Failures**: Check the job status for error details

### Logs

- Backend logs: Check the FastAPI console output
- Frontend logs: Check browser developer console

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check existing issues or create a new one 