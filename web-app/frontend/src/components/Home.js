import React from 'react';
import { Link } from 'react-router-dom';
import { Video, Brain, Target, Zap, Upload, BarChart3 } from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: <Video className="h-8 w-8 text-primary-600" />,
      title: "Video Upload",
      description: "Upload sports videos in various formats (MP4, AVI, MOV, etc.)"
    },
    {
      icon: <Brain className="h-8 w-8 text-primary-600" />,
      title: "AI Analysis",
      description: "Powered by Google's Gemini AI for comprehensive video understanding"
    },
    {
      icon: <Target className="h-8 w-8 text-primary-600" />,
      title: "Pose Detection",
      description: "Advanced pose estimation and biomechanical analysis"
    },
    {
      icon: <BarChart3 className="h-8 w-8 text-primary-600" />,
      title: "Performance Metrics",
      description: "Detailed performance analysis and improvement recommendations"
    }
  ];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <div className="flex justify-center mb-6">
          <div className="bg-primary-100 p-4 rounded-full">
            <Video className="h-16 w-16 text-primary-600" />
          </div>
        </div>
        <h1 className="text-4xl md:text-6xl font-bold text-secondary-900 mb-6">
          AI-Powered Video Analysis
        </h1>
        <p className="text-xl text-secondary-600 mb-8 max-w-3xl mx-auto">
          Transform your sports performance with cutting-edge AI technology. 
          Get detailed biomechanical analysis, technique feedback, and personalized 
          improvement recommendations.
        </p>
        <div className="flex justify-center">
          <Link
            to="/analyze"
            className="btn btn-primary inline-flex items-center space-x-2 px-8 py-3 text-lg"
          >
            <Upload className="h-5 w-5" />
            <span>Start Analysis</span>
          </Link>
        </div>
      </div>

      {/* Features Section */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
        {features.map((feature, index) => (
          <div key={index} className="card p-6 text-center">
            <div className="flex justify-center mb-4">
              {feature.icon}
            </div>
            <h3 className="text-xl font-semibold text-secondary-900 mb-2">
              {feature.title}
            </h3>
            <p className="text-secondary-600">
              {feature.description}
            </p>
          </div>
        ))}
      </div>

      {/* How It Works Section */}
      <div className="card p-8 mb-16">
        <h2 className="text-3xl font-bold text-secondary-900 mb-8 text-center">
          How It Works
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-primary-600">1</span>
            </div>
            <h3 className="text-xl font-semibold text-secondary-900 mb-2">
              Upload Video
            </h3>
            <p className="text-secondary-600">
              Upload your sports video and configure analysis settings
            </p>
          </div>
          <div className="text-center">
            <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-primary-600">2</span>
            </div>
            <h3 className="text-xl font-semibold text-secondary-900 mb-2">
              AI Processing
            </h3>
            <p className="text-secondary-600">
              Our AI analyzes pose, technique, and biomechanics
            </p>
          </div>
          <div className="text-center">
            <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-primary-600">3</span>
            </div>
            <h3 className="text-xl font-semibold text-secondary-900 mb-2">
              Get Results
            </h3>
            <p className="text-secondary-600">
              Receive detailed analysis and improvement recommendations instantly
            </p>
          </div>
        </div>
      </div>

      {/* Analysis Types Section */}
      <div className="card p-8">
        <h2 className="text-3xl font-bold text-secondary-900 mb-8 text-center">
          Analysis Types
        </h2>
        <div className="grid md:grid-cols-2 gap-8">
          <div className="border-l-4 border-primary-500 pl-6">
            <h3 className="text-xl font-semibold text-secondary-900 mb-2">
              Tennis Serve Analysis
            </h3>
            <p className="text-secondary-600 mb-4">
              Comprehensive analysis of tennis serve technique including preparation, 
              ball toss, loading phase, acceleration, contact point, and follow-through.
            </p>
            <ul className="text-sm text-secondary-500 space-y-1">
              <li>• Biomechanical assessment</li>
              <li>• Power generation analysis</li>
              <li>• Injury risk evaluation</li>
              <li>• Technique recommendations</li>
            </ul>
          </div>
          <div className="border-l-4 border-primary-500 pl-6">
            <h3 className="text-xl font-semibold text-secondary-900 mb-2">
              General Sports Analysis
            </h3>
            <p className="text-secondary-600 mb-4">
              Versatile analysis for various sports movements with focus on 
              technique quality, efficiency, and performance optimization.
            </p>
            <ul className="text-sm text-secondary-500 space-y-1">
              <li>• Movement quality assessment</li>
              <li>• Joint coordination analysis</li>
              <li>• Balance and stability evaluation</li>
              <li>• Performance optimization tips</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home; 