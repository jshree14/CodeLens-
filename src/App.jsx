import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import CodeEditor from './components/CodeEditor';
import AnalysisResults from './components/AnalysisResults';
import AnimatedBackground from './components/AnimatedBackground';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('editor');
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Track mouse movement for interactive effects
  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleAnalyze = async (code, language) => {
    setIsAnalyzing(true);
    
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          code, 
          language,
          execute: true  // Enable code execution
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAnalysisData(data);
        // Don't change view - keep showing editor with results
      } else {
        console.error('Analysis failed:', response.statusText);
        alert('Analysis failed. Please try again.');
      }
    } catch (error) {
      console.error('Error analyzing code:', error);
      alert('Error connecting to server. Please make sure the backend is running.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="app">
      <AnimatedBackground mousePosition={mousePosition} />
      
      <div className="app-content">
        <Header 
          currentView={currentView} 
          setCurrentView={setCurrentView}
          mousePosition={mousePosition}
        />

        <main className="main-content">
          <AnimatePresence mode="wait">
            {currentView === 'editor' && (
              <motion.div
                key="editor"
                className="editor-view"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <div className="split-view">
                  {/* Code Editor Section */}
                  <div className="editor-section">
                    <CodeEditor 
                      onAnalyze={handleAnalyze} 
                      isAnalyzing={isAnalyzing}
                      mousePosition={mousePosition}
                    />
                  </div>

                  {/* Results Section - Shows after analysis */}
                  {analysisData && (
                    <motion.div
                      className="results-section"
                      initial={{ opacity: 0, x: 50 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5 }}
                    >
                      <AnalysisResults 
                        data={analysisData} 
                        mousePosition={mousePosition}
                      />
                    </motion.div>
                  )}
                </div>
              </motion.div>
            )}

            {currentView === 'dashboard' && (
              <motion.div
                key="dashboard"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.1 }}
                transition={{ duration: 0.5 }}
              >
                <Dashboard mousePosition={mousePosition} />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>

      {/* Cursor follower effect */}
      <motion.div
        className="cursor-follower"
        animate={{
          x: mousePosition.x - 10,
          y: mousePosition.y - 10,
        }}
        transition={{
          type: "spring",
          stiffness: 500,
          damping: 28,
        }}
      />
    </div>
  );
}

export default App;