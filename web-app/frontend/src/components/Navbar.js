import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Video, Activity, Home } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="bg-white shadow-lg border-b border-secondary-200">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2">
            <Video className="h-8 w-8 text-primary-600" />
            <span className="text-xl font-bold text-secondary-900">
              Video Analysis AI
            </span>
          </div>
          
          <div className="flex space-x-1">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100'
              }`}
            >
              <Home className="h-4 w-4" />
              <span>Home</span>
            </Link>
            
            <Link
              to="/analyze"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/analyze') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100'
              }`}
            >
              <Activity className="h-4 w-4" />
              <span>Analyze</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 