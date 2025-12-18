import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import LogUpload from './components/LogUpload';
import RuleManagement from './components/RuleManagement';
import IaCScanner from './components/IaCScanner';
import './styles/design-system.css';

function App() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--background)' }}>
      {/* Subtle ambient glow */}
      <div 
        className="fixed inset-0 pointer-events-none"
        style={{
          background: `
            radial-gradient(circle at 20% 50%, rgba(184, 134, 11, 0.02) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(212, 168, 75, 0.015) 0%, transparent 50%)
          `
        }}
      />
      
      <Router>
        <div className="flex flex-col min-h-screen relative z-10">
          <Navbar />
          <main className="flex-grow">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/logs" element={<LogUpload />} />
              <Route path="/rules" element={<RuleManagement />} />
              <Route path="/scanner" element={<IaCScanner />} />
            </Routes>
          </main>
        </div>
      </Router>
    </div>
  );
}

export default App;