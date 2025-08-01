import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Download, 
  Clock, 
  Video, 
  Brain, 
  Target,
  AlertCircle,
  Copy,
  Check
} from 'lucide-react';
import ApiService from '../services/api';

const ResultsPage = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchJobDetails();
  }, [jobId]);

  const fetchJobDetails = async () => {
    try {
      const response = await ApiService.getJobStatus(jobId);
      setJob(response);
      setError('');
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadResults = async () => {
    try {
      const blob = await ApiService.downloadResults(jobId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analysis_results_${jobId}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      setError(error.message);
    }
  };

  const handleCopyResults = async () => {
    try {
      const analysisText = job.result?.analysis?.analysis || '';
      await navigator.clipboard.writeText(analysisText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (startDate, endDate) => {
    if (!endDate) return null;
    const start = new Date(startDate);
    const end = new Date(endDate);
    const duration = Math.round((end - start) / 1000);
    return `${duration}s`;
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="card p-8 text-center">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-secondary-900 mb-2">
            Error Loading Results
          </h3>
          <p className="text-secondary-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/jobs')}
            className="btn btn-primary"
          >
            Back to Jobs
          </button>
        </div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="card p-8 text-center">
          <AlertCircle className="h-16 w-16 text-secondary-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-secondary-900 mb-2">
            Job Not Found
          </h3>
          <p className="text-secondary-600 mb-4">
            The requested analysis job could not be found.
          </p>
          <button
            onClick={() => navigate('/jobs')}
            className="btn btn-primary"
          >
            Back to Jobs
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/jobs')}
            className="btn btn-secondary p-2"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-secondary-900">
              Analysis Results
            </h1>
            <p className="text-secondary-600">
              {job.video_filename || 'Unknown Video'}
            </p>
          </div>
        </div>
        
        {job.status === 'completed' && (
          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopyResults}
              className="btn btn-secondary inline-flex items-center space-x-2"
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4" />
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4" />
                  <span>Copy Results</span>
                </>
              )}
            </button>
            <button
              onClick={handleDownloadResults}
              className="btn btn-primary inline-flex items-center space-x-2"
            >
              <Download className="h-4 w-4" />
              <span>Download</span>
            </button>
          </div>
        )}
      </div>

      {/* Job Status */}
      <div className="card p-6 mb-8">
        <h2 className="text-xl font-semibold text-secondary-900 mb-4">
          Job Information
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="flex items-center space-x-3">
            <div className="bg-primary-100 p-2 rounded-lg">
              <Video className="h-5 w-5 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-600">Status</p>
              <p className="font-medium text-secondary-900 capitalize">
                {job.status}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="bg-primary-100 p-2 rounded-lg">
              <Clock className="h-5 w-5 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-600">Created</p>
              <p className="font-medium text-secondary-900">
                {formatDate(job.created_at)}
              </p>
            </div>
          </div>
          
          {job.completed_at && (
            <div className="flex items-center space-x-3">
              <div className="bg-primary-100 p-2 rounded-lg">
                <Target className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <p className="text-sm text-secondary-600">Duration</p>
                <p className="font-medium text-secondary-900">
                  {formatDuration(job.created_at, job.completed_at)}
                </p>
              </div>
            </div>
          )}
          
          {job.result?.analyzer_info && (
            <div className="flex items-center space-x-3">
              <div className="bg-primary-100 p-2 rounded-lg">
                <Brain className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <p className="text-sm text-secondary-600">Model</p>
                <p className="font-medium text-secondary-900">
                  {job.result.analyzer_info.gemini_model || job.result.analyzer_info.name}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Progress/Error */}
      {job.progress && job.status !== 'completed' && (
        <div className="card p-4 mb-8 bg-blue-50 border-blue-200">
          <p className="text-blue-700">
            <span className="font-medium">Progress:</span> {job.progress}
          </p>
        </div>
      )}

      {job.error && (
        <div className="card p-4 mb-8 bg-red-50 border-red-200">
          <p className="text-red-700">
            <span className="font-medium">Error:</span> {job.error}
          </p>
        </div>
      )}

      {/* Analysis Results */}
      {job.status === 'completed' && job.result?.analysis && (
        <div className="space-y-8">
          {/* Analysis Text */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-secondary-900 mb-4">
              Analysis Results
            </h2>
            
            <div className="prose max-w-none">
              <div className="bg-secondary-50 p-6 rounded-lg">
                <pre className="whitespace-pre-wrap text-sm text-secondary-800 font-mono">
                  {job.result.analysis.analysis}
                </pre>
              </div>
            </div>
          </div>

          {/* Metadata */}
          {job.result.analysis.metadata && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-secondary-900 mb-4">
                Analysis Metadata
              </h2>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {job.result.analysis.metadata.processing_time && (
                  <div className="bg-secondary-50 p-4 rounded-lg">
                    <p className="text-sm text-secondary-600">Processing Time</p>
                    <p className="font-medium text-secondary-900">
                      {job.result.analysis.metadata.processing_time.toFixed(2)}s
                    </p>
                  </div>
                )}
                
                {job.result.analysis.metadata.total_tokens && (
                  <div className="bg-secondary-50 p-4 rounded-lg">
                    <p className="text-sm text-secondary-600">Tokens Used</p>
                    <p className="font-medium text-secondary-900">
                      {job.result.analysis.metadata.total_tokens}
                    </p>
                  </div>
                )}
                
                {job.result.analysis.metadata.model_name && (
                  <div className="bg-secondary-50 p-4 rounded-lg">
                    <p className="text-sm text-secondary-600">Model</p>
                    <p className="font-medium text-secondary-900">
                      {job.result.analysis.metadata.model_name}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Raw JSON Data */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-secondary-900 mb-4">
              Raw Data
            </h2>
            
            <details className="group">
              <summary className="cursor-pointer text-primary-600 hover:text-primary-700 mb-4">
                View Raw JSON Response
              </summary>
              
              <div className="bg-secondary-900 p-4 rounded-lg overflow-x-auto">
                <pre className="text-green-400 text-sm">
                  {JSON.stringify(job.result, null, 2)}
                </pre>
              </div>
            </details>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsPage; 