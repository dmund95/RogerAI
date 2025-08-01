import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './components/Home';
import AnalysisPage from './components/AnalysisPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-secondary-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/analyze" element={<AnalysisPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 