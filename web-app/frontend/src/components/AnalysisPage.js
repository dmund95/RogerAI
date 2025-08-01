import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Upload, Settings, Play, AlertCircle, CheckCircle, FileText, Download, RotateCcw, X, ZoomIn } from 'lucide-react';
import ApiService from '../services/api';

const AnalysisPage = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysisConfig, setAnalysisConfig] = useState({
    apiKey: '',
    promptType: 'tennis',
    customPrompt: '',
    analyzer: 'gemini',
    model: 'gemini-2.0-flash-exp',
    temperature: 0.1,
    maxTokens: 8192
  });
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [extractedFrames, setExtractedFrames] = useState(null);
  const [professionalFrames, setProfessionalFrames] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  // Add modal state
  const [modalImage, setModalImage] = useState(null);
  const [modalPhaseData, setModalPhaseData] = useState(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setSelectedFile(acceptedFiles[0]);
        setError('');
      }
    },
    onDropRejected: (rejectedFiles) => {
      setError('Please select a valid video file');
    }
  });

  const handleConfigChange = (field, value) => {
    setAnalysisConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setError('Please select a video file');
      return;
    }

    if (!analysisConfig.apiKey.trim()) {
      setError('Please enter your API key');
      return;
    }

    if (analysisConfig.promptType === 'custom' && !analysisConfig.customPrompt.trim()) {
      setError('Please enter a custom prompt');
      return;
    }

    setIsAnalyzing(true);
    setError('');
    setAnalysisResult(null);
    setExtractedFrames(null);
    setProfessionalFrames(null); // Reset professional frames

    try {
      const response = await ApiService.analyzeVideo(selectedFile, analysisConfig);
      
      if (response.success) {
        setAnalysisResult(response.analysis_result);
        setExtractedFrames(response.extracted_frames || null);
        setProfessionalFrames(response.professional_frames || null); // Set professional frames
      } else {
        setError(response.error || 'Analysis failed');
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetForm = () => {
    setSelectedFile(null);
    setAnalysisResult(null);
    setExtractedFrames(null);
    setProfessionalFrames(null); // Reset professional frames
    setError('');
    setAnalysisConfig({
      apiKey: '',
      promptType: 'tennis',
      customPrompt: '',
      analyzer: 'gemini',
      model: 'gemini-2.0-flash-exp',
      temperature: 0.1,
      maxTokens: 8192
    });
  };

    const downloadResults = () => {
    if (!analysisResult) return;

    const dataStr = JSON.stringify(analysisResult, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `analysis_results_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const parseAnalysisJSON = (analysisText) => {
    // Clean up the text - remove markdown code blocks if present
    let cleanedText = analysisText.trim();
    
    // Remove markdown code block wrappers
    if (cleanedText.startsWith('```json')) {
      console.log('Detected markdown JSON code block, cleaning...');
      cleanedText = cleanedText.replace(/^```json\s*/, '').replace(/\s*```$/, '');
    } else if (cleanedText.startsWith('```')) {
      console.log('Detected markdown code block, cleaning...');
      cleanedText = cleanedText.replace(/^```\s*/, '').replace(/\s*```$/, '');
    }

    console.log('Cleaned text (first 200 chars):', cleanedText.substring(0, 200));

    try {
      const parsed = JSON.parse(cleanedText);
      console.log('Successfully parsed JSON:', parsed);
      return parsed;
    } catch (error) {
      console.error('Failed to parse analysis as JSON:', {
        error: error.message,
        originalText: analysisText.substring(0, 200) + (analysisText.length > 200 ? '...' : ''),
        cleanedText: cleanedText.substring(0, 200) + (cleanedText.length > 200 ? '...' : ''),
        fullOriginalText: analysisText,
        fullCleanedText: cleanedText
      });
      return null;
    }
  };

  const openModal = (frameUrl, phaseData, phaseName) => {
    setModalImage(`http://localhost:8000${frameUrl}`);
    setModalPhaseData({ ...phaseData, name: phaseName });
  };

  const closeModal = () => {
    setModalImage(null);
    setModalPhaseData(null);
  };

  const renderFramesDisplay = () => {
    if (!extractedFrames || Object.keys(extractedFrames).length === 0) {
      return null;
    }

    const analysisJSON = parseAnalysisJSON(analysisResult?.analysis?.analysis || '{}');
    const phases = analysisJSON?.phases || {};
    const professionalFramesData = professionalFrames || {};

    return (
      <div className="mt-6">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">
          Key Frames Analysis
        </h3>
        <div className="grid grid-cols-1 gap-6">
          {Object.entries(extractedFrames).map(([phaseName, frameUrl]) => {
            const phaseData = phases[phaseName] || {};
            const professionalFrameUrl = professionalFramesData[phaseName];
            
            return (
              <div key={phaseName} className="bg-white rounded-lg border border-secondary-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                {/* Phase Header */}
                <div className="bg-secondary-50 px-6 py-4 border-b border-secondary-200">
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold text-secondary-900 capitalize text-lg">
                      {phaseName.replace(/_/g, ' ')}
                    </h4>
                    <div className="flex items-center space-x-2">
                      {phaseData.frame_timestamp && (
                        <span className="text-sm text-secondary-600 bg-white px-2 py-1 rounded">
                          @ {phaseData.frame_timestamp}
                        </span>
                      )}
                      {phaseData.score !== undefined && (
                        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          phaseData.score >= 8 ? 'bg-green-100 text-green-800' :
                          phaseData.score >= 6 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {phaseData.score}/10
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Image Comparison */}
                <div className="grid md:grid-cols-2 gap-4 p-6">
                  {/* Your Video Frame */}
                  <div className="space-y-3">
                    <div className="text-center">
                      <h5 className="text-sm font-medium text-secondary-700 mb-2">Your Technique</h5>
                      <div className="bg-secondary-100 relative group cursor-pointer rounded-lg overflow-hidden flex items-center justify-center" onClick={() => openModal(frameUrl, phaseData, phaseName)}>
                        <img
                          src={`http://localhost:8000${frameUrl}`}
                          alt={`${phaseName} phase - your technique`}
                          className="w-full h-auto object-contain"
                          onError={(e) => {
                            e.target.src = '/api/placeholder/400/300';
                            e.target.alt = 'Frame not available';
                          }}
                        />
                        {/* Overlay for hover effect */}
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                          <ZoomIn className="h-8 w-8 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Professional Frame */}
                  <div className="space-y-3">
                    <div className="text-center">
                      <h5 className="text-sm font-medium text-secondary-700 mb-2">Professional Reference</h5>
                      {professionalFrameUrl ? (
                        <div className="bg-secondary-100 relative group cursor-pointer rounded-lg overflow-hidden flex items-center justify-center" onClick={() => openModal(professionalFrameUrl, phaseData, `${phaseName} (Professional)`)}>
                          <img
                            src={`http://localhost:8000${professionalFrameUrl}`}
                            alt={`${phaseName} phase - professional technique`}
                            className="w-full h-auto object-contain"
                            onError={(e) => {
                              e.target.src = '/api/placeholder/400/300';
                              e.target.alt = 'Professional frame not available';
                            }}
                          />
                          {/* Overlay for hover effect */}
                          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                            <ZoomIn className="h-8 w-8 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                          </div>
                        </div>
                      ) : (
                        <div className="bg-secondary-100 rounded-lg p-8 flex items-center justify-center text-secondary-500">
                          <span className="text-sm">Professional reference not available</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Analysis Details */}
                <div className="px-6 pb-6">
                  {phaseData.feedback && (
                    <div className="mb-3">
                      <p className="text-secondary-700 text-sm leading-relaxed">
                        {phaseData.feedback}
                      </p>
                    </div>
                  )}
                  
                  {phaseData.observations && phaseData.observations.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-secondary-900 mb-2">Key Observations:</p>
                      <ul className="text-sm text-secondary-600 space-y-1">
                        {phaseData.observations.slice(0, 3).map((obs, idx) => (
                          <li key={idx} className="flex items-start">
                            <span className="text-primary-500 mr-2">•</span>
                            <span>{obs}</span>
                          </li>
                        ))}
                        {phaseData.observations.length > 3 && (
                          <li className="text-xs text-secondary-500 italic">
                            +{phaseData.observations.length - 3} more observations (click to view all)
                          </li>
                        )}
                      </ul>
                    </div>
                  )}
                  
                  <div className="mt-3 pt-3 border-t border-secondary-100">
                    <button
                      onClick={() => openModal(frameUrl, phaseData, phaseName)}
                      className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center space-x-1"
                    >
                      <ZoomIn className="h-4 w-4" />
                      <span>View Full Analysis</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderStructuredAnalysis = () => {
    if (!analysisResult || !analysisResult.analysis || !analysisResult.analysis.analysis) {
      return null;
    }

    const analysisJSON = parseAnalysisJSON(analysisResult.analysis.analysis);
    if (!analysisJSON || !analysisJSON.phases) {
      return (
        <div className="bg-secondary-50 rounded-lg p-6 max-h-96 overflow-y-auto">
          <div className="prose max-w-none">
            {formatAnalysisText(analysisResult.analysis.analysis)}
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Overall Score */}
        {analysisJSON.overall_score && (
          <div className="bg-primary-50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-primary-900">Overall Score</h3>
              <span className="text-2xl font-bold text-primary-600">
                {analysisJSON.overall_score}/10
              </span>
            </div>
          </div>
        )}

        {/* Phases Analysis
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-secondary-900">Phase Analysis</h3>
          <div className="grid gap-4">
            {Object.entries(analysisJSON.phases).map(([phaseName, phaseData]) => (
              <div key={phaseName} className="bg-white border border-secondary-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <h4 className="font-medium text-secondary-900 capitalize">
                    {phaseName.replace(/_/g, ' ')}
                  </h4>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-secondary-600">
                      @ {phaseData.frame_timestamp}
                    </span>
                    <span className={`px-2 py-1 rounded text-sm font-medium ${
                      phaseData.score >= 8 ? 'bg-green-100 text-green-800' :
                      phaseData.score >= 6 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {phaseData.score}/10
                    </span>
                  </div>
                </div>
                <p className="text-secondary-700 mb-2">{phaseData.feedback}</p>
                {phaseData.observations && (
                  <div>
                    <p className="text-sm font-medium text-secondary-900 mb-1">Observations:</p>
                    <ul className="text-sm text-secondary-600 list-disc list-inside">
                      {phaseData.observations.map((obs, idx) => (
                        <li key={idx}>{obs}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div> */}

        {/* Recommendations */}
        {analysisJSON.recommendations && (
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">Recommendations</h3>
            <div className="space-y-3">
              {analysisJSON.recommendations.improvement_areas && (
                <div>
                  <p className="font-medium text-blue-800">Areas for Improvement:</p>
                  <ul className="text-blue-700 list-disc list-inside mt-1">
                    {analysisJSON.recommendations.improvement_areas.map((area, idx) => (
                      <li key={idx}>{area}</li>
                    ))}
                  </ul>
                </div>
              )}
              {analysisJSON.recommendations.technical_adjustments && (
                <div>
                  <p className="font-medium text-blue-800">Technical Adjustments:</p>
                  <ul className="text-blue-700 list-disc list-inside mt-1">
                    {analysisJSON.recommendations.technical_adjustments.map((adj, idx) => (
                      <li key={idx}>{adj}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Biomechanical Summary */}
        {analysisJSON.biomechanical_summary && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-secondary-900 mb-3">Biomechanical Summary</h3>
            <div className="grid md:grid-cols-2 gap-4">
              {analysisJSON.biomechanical_summary.strengths && (
                <div>
                  <p className="font-medium text-green-800">Strengths:</p>
                  <ul className="text-secondary-700 list-disc list-inside mt-1">
                    {analysisJSON.biomechanical_summary.strengths.map((strength, idx) => (
                      <li key={idx}>{strength}</li>
                    ))}
                  </ul>
                </div>
              )}
              {analysisJSON.biomechanical_summary.weaknesses && (
                <div>
                  <p className="font-medium text-red-800">Weaknesses:</p>
                  <ul className="text-secondary-700 list-disc list-inside mt-1">
                    {analysisJSON.biomechanical_summary.weaknesses.map((weakness, idx) => (
                      <li key={idx}>{weakness}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            {/* {analysisJSON.biomechanical_summary.efficiency_rating && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-secondary-900">Efficiency Rating:</span>
                  <span className="text-lg font-semibold text-primary-600">
                    {analysisJSON.biomechanical_summary.efficiency_rating}/10
                  </span>
                </div>
              </div>
            )} */}
          </div>
        )}
      </div>
    );
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatAnalysisText = (text) => {
    text = text.analysis;
    if (!text || typeof text !== 'string') return '';
    
    // Split by double newlines to create paragraphs
    const paragraphs = text.split('\n\n');
    
    return paragraphs.map((paragraph, index) => {
      // Check if this is a heading (starts with ** or #)
      if (paragraph.startsWith('**') && paragraph.endsWith('**')) {
        return (
          <h3 key={index} className="text-lg font-semibold text-secondary-900 mt-4 mb-2">
            {paragraph.replace(/\*\*/g, '')}
          </h3>
        );
      } else if (paragraph.startsWith('# ')) {
        return (
          <h2 key={index} className="text-xl font-bold text-secondary-900 mt-6 mb-3">
            {paragraph.replace(/^# /, '')}
          </h2>
        );
      } else if (paragraph.startsWith('## ')) {
        return (
          <h3 key={index} className="text-lg font-semibold text-secondary-900 mt-4 mb-2">
            {paragraph.replace(/^## /, '')}
          </h3>
        );
      } else if (paragraph.startsWith('### ')) {
        return (
          <h4 key={index} className="text-md font-medium text-secondary-900 mt-3 mb-2">
            {paragraph.replace(/^### /, '')}
          </h4>
        );
      } else if (paragraph.startsWith('- ')) {
        // Handle bullet points
        const items = paragraph.split('\n');
        return (
          <ul key={index} className="list-disc list-inside space-y-1 mb-4">
            {items.map((item, itemIndex) => (
              <li key={itemIndex} className="text-secondary-700">
                {item.replace(/^- /, '')}
              </li>
            ))}
          </ul>
        );
      } else {
        return (
          <p key={index} className="text-secondary-700 leading-relaxed mb-4">
            {paragraph}
          </p>
        );
      }
    });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-secondary-900 mb-2">
          Video Analysis
        </h1>
        <p className="text-secondary-600">
          Upload your sports video and get instant AI analysis
        </p>
      </div>

      {/* Analysis Results Section */}
      {analysisResult && (
        <div className="card p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-secondary-900 flex items-center">
              <FileText className="h-5 w-5 mr-2" />
              Analysis Results
            </h2>
            <div className="flex space-x-2">
              <button
                onClick={downloadResults}
                className="btn btn-secondary inline-flex items-center space-x-2"
              >
                <Download className="h-4 w-4" />
                <span>Download</span>
              </button>
              <button
                onClick={resetForm}
                className="btn btn-secondary inline-flex items-center space-x-2"
              >
                <RotateCcw className="h-4 w-4" />
                <span>New Analysis</span>
              </button>
            </div>
          </div>
          
          {renderStructuredAnalysis()}
          
          {/* Display extracted frames */}
          {renderFramesDisplay()}
          
          {analysisResult.metadata && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-secondary-900 mb-2">Analysis Metadata</h3>
              <div className="text-xs text-secondary-600 space-y-1">
                {analysisResult.metadata.video_info && (
                  <div>
                    <strong>Video:</strong> {analysisResult.metadata.video_info.width}x{analysisResult.metadata.video_info.height} 
                    @ {analysisResult.metadata.video_info.fps}fps, {analysisResult.metadata.video_info.duration}s
                  </div>
                )}
                {analysisResult.metadata.pose_keypoints_count && (
                  <div>
                    <strong>Pose Keypoints:</strong> {analysisResult.metadata.pose_keypoints_count} frames analyzed
                  </div>
                )}
                {analysisResult.metadata.analysis_timestamp && (
                  <div>
                    <strong>Analyzed:</strong> {new Date(analysisResult.metadata.analysis_timestamp).toLocaleString()}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Form Section - Hidden when showing results */}
      {!analysisResult && (
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Video Upload Section */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-secondary-900 mb-4">
              Upload Video
            </h2>
            
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-primary-500 bg-primary-50'
                  : selectedFile
                  ? 'border-green-500 bg-green-50'
                  : 'border-secondary-300 hover:border-primary-400'
              }`}
            >
              <input {...getInputProps()} />
              
              {selectedFile ? (
                <div className="space-y-2">
                  <CheckCircle className="h-12 w-12 text-green-500 mx-auto" />
                  <p className="text-lg font-medium text-secondary-900">
                    {selectedFile.name}
                  </p>
                  <p className="text-secondary-600">
                    {formatFileSize(selectedFile.size)}
                  </p>
                  <p className="text-sm text-secondary-500">
                    Click or drag to replace
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  <Upload className="h-12 w-12 text-secondary-400 mx-auto" />
                  <p className="text-lg font-medium text-secondary-900">
                    {isDragActive ? 'Drop video here' : 'Drag & drop video here'}
                  </p>
                  <p className="text-secondary-600">
                    or click to select file
                  </p>
                  <p className="text-sm text-secondary-500">
                    Supports MP4, AVI, MOV, MKV, WMV, FLV, WEBM
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* API Key Section */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-secondary-900 mb-4">
              API Configuration
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  API Key *
                </label>
                <input
                  type="password"
                  value={analysisConfig.apiKey}
                  onChange={(e) => handleConfigChange('apiKey', e.target.value)}
                  placeholder="Enter your Gemini API key"
                  className="input"
                  required
                />
                <p className="text-xs text-secondary-500 mt-1">
                  Get your API key from{' '}
                  <a
                    href="https://ai.google.dev/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700"
                  >
                    Google AI Studio
                  </a>
                </p>
              </div>
            </div>
          </div>

          {/* Analysis Configuration */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-secondary-900 mb-4">
              Analysis Configuration
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Analysis Type
                </label>
                <select
                  value={analysisConfig.promptType}
                  onChange={(e) => handleConfigChange('promptType', e.target.value)}
                  className="input"
                >
                  <option value="tennis">Tennis Serve Analysis</option>
                  <option value="general">General Sports Analysis</option>
                  <option value="custom">Custom Analysis</option>
                </select>
              </div>

              {analysisConfig.promptType === 'custom' && (
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Custom Prompt
                  </label>
                  <textarea
                    value={analysisConfig.customPrompt}
                    onChange={(e) => handleConfigChange('customPrompt', e.target.value)}
                    placeholder="Enter your custom analysis prompt..."
                    rows={4}
                    className="input"
                  />
                </div>
              )}

              <div>
                <button
                  type="button"
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className="flex items-center space-x-2 text-primary-600 hover:text-primary-700"
                >
                  <Settings className="h-4 w-4" />
                  <span>Advanced Settings</span>
                </button>
              </div>

              {showAdvanced && (
                <div className="space-y-4 pt-4 border-t border-secondary-200">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        Model
                      </label>
                      <select
                        value={analysisConfig.model}
                        onChange={(e) => handleConfigChange('model', e.target.value)}
                        className="input"
                      >
                        <option value="gemini-2.0-flash-exp">Gemini 2.0 Flash (Experimental)</option>
                        <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        Temperature ({analysisConfig.temperature})
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={analysisConfig.temperature}
                        onChange={(e) => handleConfigChange('temperature', parseFloat(e.target.value))}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-secondary-500">
                        <span>Focused</span>
                        <span>Creative</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      Max Tokens
                    </label>
                    <input
                      type="number"
                      value={analysisConfig.maxTokens}
                      onChange={(e) => handleConfigChange('maxTokens', parseInt(e.target.value))}
                      min="1000"
                      max="32768"
                      className="input"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="card p-4 bg-red-50 border-red-200">
              <div className="flex items-center space-x-2 text-red-700">
                <AlertCircle className="h-5 w-5" />
                <span>{error}</span>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-center">
            <button
              type="submit"
              disabled={isAnalyzing || !selectedFile}
              className={`btn btn-primary inline-flex items-center space-x-2 px-8 py-3 text-lg ${
                isAnalyzing || !selectedFile ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isAnalyzing ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Play className="h-5 w-5" />
                  <span>Start Analysis</span>
                </>
              )}
            </button>
          </div>
        </form>
      )}

      {/* Modal for Frame Preview */}
      {modalImage && modalPhaseData && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" onClick={closeModal}>
          <div className="bg-white rounded-lg max-w-[95vw] max-h-[95vh] overflow-y-auto m-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between p-4 border-b border-secondary-200">
              <h3 className="text-xl font-semibold text-secondary-900 capitalize">
                {modalPhaseData.name?.replace(/_/g, ' ').replace(' (Professional)', '')} Analysis
              </h3>
              <button
                onClick={closeModal}
                className="text-secondary-400 hover:text-secondary-600 transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="p-6">
              <div className="grid lg:grid-cols-3 gap-6">
                {/* Images Comparison */}
                <div className="lg:col-span-2 space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    {/* User Frame */}
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-secondary-700 text-center">Your Technique</h4>
                      <div className="bg-secondary-100 rounded-lg overflow-hidden flex items-center justify-center">
                        {extractedFrames && modalPhaseData.name && extractedFrames[modalPhaseData.name.replace(' (Professional)', '')] && (
                          <img
                            src={`http://localhost:8000${extractedFrames[modalPhaseData.name.replace(' (Professional)', '')]}`}
                            alt={`${modalPhaseData.name} phase - user technique`}
                            className="w-full h-auto object-contain"
                            onError={(e) => {
                              e.target.src = '/api/placeholder/600/400';
                              e.target.alt = 'User frame not available';
                            }}
                          />
                        )}
                      </div>
                    </div>
                    
                    {/* Professional Frame */}
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-secondary-700 text-center">Professional Reference</h4>
                      <div className="bg-secondary-100 rounded-lg overflow-hidden flex items-center justify-center">
                        {professionalFrames && modalPhaseData.name && professionalFrames[modalPhaseData.name.replace(' (Professional)', '')] ? (
                          <img
                            src={`http://localhost:8000${professionalFrames[modalPhaseData.name.replace(' (Professional)', '')]}`}
                            alt={`${modalPhaseData.name} phase - professional technique`}
                            className="w-full h-auto object-contain"
                            onError={(e) => {
                              e.target.src = '/api/placeholder/600/400';
                              e.target.alt = 'Professional frame not available';
                            }}
                          />
                        ) : (
                          <div className="w-full h-48 flex items-center justify-center text-secondary-500">
                            <span className="text-sm">Professional reference not available</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {modalPhaseData.frame_timestamp && (
                    <div className="text-center">
                      <span className="inline-block bg-secondary-100 text-secondary-700 px-3 py-1 rounded-full text-sm font-medium">
                        Timestamp: {modalPhaseData.frame_timestamp}
                      </span>
                    </div>
                  )}
                </div>
                
                {/* Analysis Details */}
                <div className="space-y-4">
                  {/* Score */}
                  {modalPhaseData.score !== undefined && (
                    <div className="bg-secondary-50 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <h4 className="text-lg font-semibold text-secondary-900">Phase Score</h4>
                        <span className={`px-4 py-2 rounded-full text-lg font-bold ${
                          modalPhaseData.score >= 8 ? 'bg-green-100 text-green-800' :
                          modalPhaseData.score >= 6 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {modalPhaseData.score}/10
                        </span>
                      </div>
                    </div>
                  )}
                  
                  {/* Feedback */}
                  {modalPhaseData.feedback && (
                    <div>
                      <h4 className="text-lg font-semibold text-secondary-900 mb-2">Feedback</h4>
                      <div className="bg-blue-50 rounded-lg p-4">
                        <p className="text-secondary-700 leading-relaxed">
                          {modalPhaseData.feedback}
                        </p>
                      </div>
                    </div>
                  )}
                  
                  {/* Observations */}
                  {modalPhaseData.observations && modalPhaseData.observations.length > 0 && (
                    <div>
                      <h4 className="text-lg font-semibold text-secondary-900 mb-2">
                        Detailed Observations
                      </h4>
                      <div className="bg-gray-50 rounded-lg p-4">
                        <ul className="space-y-2">
                          {modalPhaseData.observations.map((obs, idx) => (
                            <li key={idx} className="flex items-start">
                              <span className="text-primary-500 mr-2 mt-1">•</span>
                              <span className="text-secondary-700">{obs}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                  
                  {/* Technical Details if available */}
                  {modalPhaseData.technical_notes && (
                    <div>
                      <h4 className="text-lg font-semibold text-secondary-900 mb-2">Technical Notes</h4>
                      <div className="bg-yellow-50 rounded-lg p-4">
                        <p className="text-secondary-700">
                          {modalPhaseData.technical_notes}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="mt-6 pt-4 border-t border-secondary-200 text-center">
                <button
                  onClick={closeModal}
                  className="btn btn-secondary px-6"
                >
                  Close Analysis
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisPage; 