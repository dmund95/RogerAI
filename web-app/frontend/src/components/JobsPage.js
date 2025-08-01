import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  Play, 
  Download, 
  Trash2, 
  RefreshCw,
  Eye,
  AlertCircle
} from 'lucide-react';
import ApiService from '../services/api';

const JobsPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const highlightJobId = searchParams.get('highlight');
  
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pollingJobs, setPollingJobs] = useState(new Set());

  useEffect(() => {
    fetchJobs();
    
    // Set up polling for active jobs
    const interval = setInterval(() => {
      fetchJobs();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await ApiService.getAllJobs();
      setJobs(response.jobs || []);
      setError('');
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteJob = async (jobId) => {
    if (!window.confirm('Are you sure you want to delete this job?')) {
      return;
    }

    try {
      await ApiService.deleteJob(jobId);
      setJobs(jobs.filter(job => job.job_id !== jobId));
    } catch (error) {
      setError(error.message);
    }
  };

  const handleDownloadResults = async (jobId) => {
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

  const handleViewResults = (jobId) => {
    navigate(`/results/${jobId}`);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'queued':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'processing':
        return <Play className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'queued':
        return 'bg-yellow-100 text-yellow-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
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

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">
            Analysis Jobs
          </h1>
          <p className="text-secondary-600">
            Track and manage your video analysis jobs
          </p>
        </div>
        
        <button
          onClick={fetchJobs}
          className="btn btn-secondary inline-flex items-center space-x-2"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="card p-4 bg-red-50 border-red-200 mb-6">
          <div className="flex items-center space-x-2 text-red-700">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {jobs.length === 0 ? (
        <div className="card p-8 text-center">
          <div className="mb-4">
            <Play className="h-16 w-16 text-secondary-400 mx-auto" />
          </div>
          <h3 className="text-xl font-semibold text-secondary-900 mb-2">
            No analysis jobs yet
          </h3>
          <p className="text-secondary-600 mb-4">
            Start by uploading a video for analysis
          </p>
          <button
            onClick={() => navigate('/analyze')}
            className="btn btn-primary"
          >
            Start Analysis
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs.map((job) => (
            <div
              key={job.job_id}
              className={`card p-6 ${
                highlightJobId === job.job_id ? 'ring-2 ring-primary-500' : ''
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {getStatusIcon(job.status)}
                  <div>
                    <h3 className="text-lg font-semibold text-secondary-900">
                      {job.video_filename || 'Unknown Video'}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-secondary-600">
                      <span>Created: {formatDate(job.created_at)}</span>
                      {job.completed_at && (
                        <span>
                          Duration: {formatDuration(job.created_at, job.completed_at)}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                      job.status
                    )}`}
                  >
                    {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                  </span>
                  
                  <div className="flex items-center space-x-2">
                    {job.status === 'completed' && (
                      <>
                        <button
                          onClick={() => handleViewResults(job.job_id)}
                          className="btn btn-secondary p-2"
                          title="View Results"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDownloadResults(job.job_id)}
                          className="btn btn-secondary p-2"
                          title="Download Results"
                        >
                          <Download className="h-4 w-4" />
                        </button>
                      </>
                    )}
                    
                    <button
                      onClick={() => handleDeleteJob(job.job_id)}
                      className="btn btn-danger p-2"
                      title="Delete Job"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
              
              {job.progress && (
                <div className="mt-4 p-3 bg-secondary-50 rounded-lg">
                  <p className="text-sm text-secondary-700">
                    <span className="font-medium">Progress:</span> {job.progress}
                  </p>
                </div>
              )}
              
              {job.error && (
                <div className="mt-4 p-3 bg-red-50 rounded-lg">
                  <p className="text-sm text-red-700">
                    <span className="font-medium">Error:</span> {job.error}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default JobsPage; 