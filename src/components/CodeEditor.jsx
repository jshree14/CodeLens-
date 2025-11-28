import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Sparkles, Code } from 'lucide-react';
import './CodeEditor.css';

const CodeEditor = ({ onAnalyze, isAnalyzing, mousePosition }) => {
  const [code, setCode] = useState(`def factorial(n):
    """Calculate factorial of a number"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Test the function
print(factorial(5))`);

  const [language, setLanguage] = useState('python');

  const languages = [
    { value: 'python', label: 'Python', color: '#3776ab' },
    { value: 'javascript', label: 'JavaScript', color: '#f7df1e' },
    { value: 'java', label: 'Java', color: '#007396' },
    { value: 'cpp', label: 'C++', color: '#00599c' },
  ];

  const handleAnalyze = () => {
    if (code.trim()) {
      onAnalyze(code, language);
    }
  };

  return (
    <div className="code-editor-container">
      <motion.div
        className="editor-card glass"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="editor-header">
          <div className="editor-title">
            <Code className="title-icon" size={24} />
            <h2 className="gradient-text">Code Editor</h2>
          </div>

          {/* Language Selector */}
          <div className="language-selector">
            {languages.map((lang) => (
              <motion.button
                key={lang.value}
                className={`lang-btn ${language === lang.value ? 'active' : ''}`}
                onClick={() => setLanguage(lang.value)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                style={{
                  '--lang-color': lang.color,
                }}
              >
                {lang.label}
              </motion.button>
            ))}
          </div>
        </div>

        {/* Code Input */}
        <div className="editor-body">
          <div className="line-numbers">
            {code.split('\n').map((_, i) => (
              <div key={i} className="line-number">
                {i + 1}
              </div>
            ))}
          </div>

          <textarea
            className="code-input"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your code here..."
            spellCheck={false}
          />
        </div>

        {/* Footer */}
        <div className="editor-footer">
          <div className="code-stats">
            <span>{code.split('\n').length} lines</span>
            <span>•</span>
            <span>{code.length} characters</span>
          </div>

          <motion.button
            className="analyze-btn btn-primary"
            onClick={handleAnalyze}
            disabled={isAnalyzing || !code.trim()}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isAnalyzing ? (
              <>
                <div className="spinner" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Sparkles size={20} />
                <span>Analyze Code</span>
                <Play size={16} />
              </>
            )}
          </motion.button>
        </div>
      </motion.div>

      {/* Floating Hints */}
      <motion.div
        className="floating-hint glass"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Sparkles size={16} className="hint-icon" />
        <p>Paste your code and click Analyze to get AI-powered insights!</p>
      </motion.div>
    </div>
  );
};

export default CodeEditor;