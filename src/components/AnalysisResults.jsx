import React from 'react';
import { motion } from 'framer-motion';
import { 
  AlertCircle, 
  AlertTriangle, 
  Info, 
  CheckCircle, 
  Code, 
  TrendingUp,
  Shield,
  Zap,
  FileCode,
  BarChart3,
  Play
} from 'lucide-react';
import './AnalysisResults.css';

const AnalysisResults = ({ data }) => {
  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'error':
        return <AlertCircle className="severity-icon error" />;
      case 'warning':
        return <AlertTriangle className="severity-icon warning" />;
      case 'info':
        return <Info className="severity-icon info" />;
      default:
        return <CheckCircle className="severity-icon success" />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'error':
      case 'critical':
        return 'severity-error';
      case 'warning':
      case 'high':
        return 'severity-warning';
      case 'info':
      case 'medium':
        return 'severity-info';
      default:
        return 'severity-success';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'priority-high';
      case 'medium':
        return 'priority-medium';
      case 'low':
        return 'priority-low';
      default:
        return 'priority-medium';
    }
  };

  return (
    <div className="analysis-results-container">
      {/* Header with Score */}
      <motion.div
        className="results-header glass"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="header-content">
          <div className="header-left">
            <FileCode className="header-icon" size={32} />
            <div>
              <h2 className="gradient-text">Analysis Complete</h2>
              <p className="language-badge">{data.language}</p>
            </div>
          </div>
          <div className="score-display">
            <div className="score-circle">
              <svg className="score-ring" viewBox="0 0 100 100">
                <circle
                  className="score-ring-bg"
                  cx="50"
                  cy="50"
                  r="45"
                />
                <circle
                  className="score-ring-progress"
                  cx="50"
                  cy="50"
                  r="45"
                  style={{
                    strokeDasharray: `${data.summary.score * 2.827} 282.7`,
                  }}
                />
              </svg>
              <div className="score-value">
                <span className="score-number">{data.summary.score}</span>
                <span className="score-label">/100</span>
              </div>
            </div>
            <div className="score-text">
              <p className="score-title">Quality Score</p>
              <p className="score-description">
                {data.summary.score >= 90 ? 'Excellent' :
                 data.summary.score >= 80 ? 'Good' :
                 data.summary.score >= 70 ? 'Fair' :
                 data.summary.score >= 60 ? 'Needs Work' : 'Poor'}
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Code Execution Output */}
      {data.execution && (
        <motion.div
          className="results-section glass"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.05 }}
        >
          <div className="section-header">
            <Play size={24} />
            <h3>Execution Output</h3>
            <span className={`execution-badge ${data.execution.success ? 'success' : 'error'}`}>
              {data.execution.success ? 'Success' : 'Failed'}
            </span>
            <span className="execution-time">{data.execution.execution_time}s</span>
          </div>
          
          {data.execution.output && (
            <div className="execution-output">
              <strong>Output:</strong>
              <pre className="output-text">{data.execution.output}</pre>
            </div>
          )}
          
          {data.execution.error && (
            <div className="execution-error">
              <strong>Error:</strong>
              <pre className="error-text">{data.execution.error}</pre>
            </div>
          )}
          
          {!data.execution.output && !data.execution.error && (
            <p className="no-output">No output generated</p>
          )}
        </motion.div>
      )}

      {/* Purpose & Overview */}
      <motion.div
        className="results-section glass"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <div className="section-header">
          <Code size={24} />
          <h3>Code Purpose</h3>
        </div>
        <p className="purpose-text">{data.summary.purpose}</p>
        <p className="overview-text">{data.summary.overview}</p>
      </motion.div>

      {/* Metrics */}
      {data.metrics && (
        <motion.div
          className="results-section glass"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="section-header">
            <BarChart3 size={24} />
            <h3>Code Metrics</h3>
          </div>
          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-label">Lines</span>
              <span className="metric-value">{data.metrics.lines || data.metrics.total_lines || 0}</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">Functions</span>
              <span className="metric-value">{data.metrics.functions || 0}</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">Classes</span>
              <span className="metric-value">{data.metrics.classes || 0}</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">Complexity</span>
              <span className="metric-value">{data.metrics.complexity || 1}</span>
            </div>
            {data.metrics.loops !== undefined && (
              <div className="metric-card">
                <span className="metric-label">Loops</span>
                <span className="metric-value">{data.metrics.loops}</span>
              </div>
            )}
            {data.metrics.conditions !== undefined && (
              <div className="metric-card">
                <span className="metric-label">Conditions</span>
                <span className="metric-value">{data.metrics.conditions}</span>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Issues & Errors */}
      {data.issues && data.issues.length > 0 && (
        <motion.div
          className="results-section glass"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="section-header">
            <AlertTriangle size={24} />
            <h3>Issues Found ({data.issues.length})</h3>
          </div>
          <div className="issues-list">
            {data.issues.map((issue, index) => (
              <motion.div
                key={index}
                className={`issue-card ${getSeverityColor(issue.severity)}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + index * 0.05 }}
              >
                <div className="issue-header">
                  {getSeverityIcon(issue.severity)}
                  <div className="issue-title-section">
                    <h4 className="issue-title">{issue.title}</h4>
                    <span className={`issue-badge ${getSeverityColor(issue.severity)}`}>
                      {issue.severity}
                    </span>
                    {issue.source && (
                      <span className="issue-source">{issue.source}</span>
                    )}
                  </div>
                </div>
                <p className="issue-description">{issue.description}</p>
                {issue.suggestion && (
                  <div className="issue-suggestion">
                    <strong>💡 Suggestion:</strong> {issue.suggestion}
                  </div>
                )}
                {issue.line_number && (
                  <div className="issue-line">
                    <Code size={14} /> Line {issue.line_number}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Improvements */}
      {data.improvements && data.improvements.length > 0 && (
        <motion.div
          className="results-section glass"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <div className="section-header">
            <TrendingUp size={24} />
            <h3>Improvement Suggestions ({data.improvements.length})</h3>
          </div>
          <div className="improvements-list">
            {data.improvements.map((improvement, index) => (
              <motion.div
                key={index}
                className={`improvement-card ${getPriorityColor(improvement.priority)}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.05 }}
              >
                <div className="improvement-header">
                  <TrendingUp size={20} />
                  <h4 className="improvement-title">{improvement.title}</h4>
                  <span className={`priority-badge ${getPriorityColor(improvement.priority)}`}>
                    {improvement.priority}
                  </span>
                </div>
                <p className="improvement-description">{improvement.description}</p>
                <div className="improvement-suggestion">
                  <strong>✨ How to improve:</strong> {improvement.suggestion}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Security Concerns */}
      {data.security_concerns && data.security_concerns.length > 0 && (
        <motion.div
          className="results-section glass"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <div className="section-header">
            <Shield size={24} />
            <h3>Security Concerns ({data.security_concerns.length})</h3>
          </div>
          <div className="security-list">
            {data.security_concerns.map((concern, index) => (
              <motion.div
                key={index}
                className={`security-card ${getSeverityColor(concern.severity)}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + index * 0.05 }}
              >
                <div className="security-header">
                  <Shield size={20} />
                  <h4 className="security-title">{concern.title}</h4>
                  <span className={`severity-badge ${getSeverityColor(concern.severity)}`}>
                    {concern.severity}
                  </span>
                </div>
                <p className="security-description">{concern.description}</p>
                <div className="security-mitigation">
                  <strong>🛡️ Mitigation:</strong> {concern.mitigation}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Performance Notes */}
      {data.performance_notes && data.performance_notes.length > 0 && (
        <motion.div
          className="results-section glass"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <div className="section-header">
            <Zap size={24} />
            <h3>Performance Optimization ({data.performance_notes.length})</h3>
          </div>
          <div className="performance-list">
            {data.performance_notes.map((note, index) => (
              <motion.div
                key={index}
                className="performance-card"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7 + index * 0.05 }}
              >
                <div className="performance-header">
                  <Zap size={20} />
                  <h4 className="performance-title">{note.title}</h4>
                </div>
                <p className="performance-description">{note.description}</p>
                <div className="performance-suggestion">
                  <strong>⚡ Optimization:</strong> {note.suggestion}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Summary Footer */}
      <motion.div
        className="results-footer glass"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.8 }}
      >
        <div className="footer-stats">
          <div className="stat">
            <AlertCircle size={16} />
            <span>{data.issues?.length || 0} Issues</span>
          </div>
          <div className="stat">
            <TrendingUp size={16} />
            <span>{data.improvements?.length || 0} Improvements</span>
          </div>
          <div className="stat">
            <Shield size={16} />
            <span>{data.security_concerns?.length || 0} Security</span>
          </div>
          <div className="stat">
            <Zap size={16} />
            <span>{data.performance_notes?.length || 0} Performance</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default AnalysisResults;