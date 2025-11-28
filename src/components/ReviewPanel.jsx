import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  FileText, 
  AlertTriangle, 
  BarChart3, 
  Loader2,
  CheckCircle,
  XCircle,
  Info
} from 'lucide-react'
import ScoreGauge from './ScoreGauge'
import MetricsChart from './MetricsChart'

const TABS = [
  { id: 'summary', label: 'Summary', icon: FileText },
  { id: 'issues', label: 'Issues & Suggestions', icon: AlertTriangle },
  { id: 'metrics', label: 'Score & Metrics', icon: BarChart3 },
]

const ReviewPanel = ({ analysis, isAnalyzing }) => {
  const [activeTab, setActiveTab] = useState('summary')

  const renderLoadingState = () => (
    <motion.div 
      className="flex flex-col items-center justify-center h-64 space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <Loader2 className="w-12 h-12 text-primary-600 animate-spin" />
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          Analyzing your code...
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          This may take a few seconds
        </p>
      </div>
      <div className="w-48 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <motion.div 
          className="bg-primary-600 h-2 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: '100%' }}
          transition={{ duration: 3, repeat: Infinity }}
        />
      </div>
    </motion.div>
  )

  const renderEmptyState = () => (
    <motion.div 
      className="flex flex-col items-center justify-center h-64 space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-full">
        <FileText className="w-12 h-12 text-gray-400" />
      </div>
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          Ready for Analysis
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Enter your code and click "Analyze Code" to get started
        </p>
      </div>
    </motion.div>
  )

  const renderSummary = () => (
    <motion.div 
      className="space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="card p-4">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
          Code Purpose
        </h3>
        <p className="text-gray-700 dark:text-gray-300">
          {analysis?.summary?.purpose || 'No summary available'}
        </p>
      </div>
      
      <div className="card p-4">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
          Overview
        </h3>
        <p className="text-gray-700 dark:text-gray-300">
          {analysis?.summary?.overview || 'No overview available'}
        </p>
      </div>
      
      {analysis?.summary?.score && (
        <div className="card p-4">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
            Overall Score
          </h3>
          <ScoreGauge score={analysis.summary.score} />
        </div>
      )}
    </motion.div>
  )

  const renderIssues = () => (
    <motion.div 
      className="space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {analysis?.issues?.map((issue, index) => (
        <motion.div 
          key={index}
          className="card p-4"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          <div className="flex items-start space-x-3">
            <div className={`p-1 rounded-full ${
              issue.severity === 'error' ? 'bg-red-100 dark:bg-red-900' :
              issue.severity === 'warning' ? 'bg-yellow-100 dark:bg-yellow-900' :
              'bg-blue-100 dark:bg-blue-900'
            }`}>
              {issue.severity === 'error' ? (
                <XCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
              ) : issue.severity === 'warning' ? (
                <AlertTriangle className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
              ) : (
                <Info className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              )}
            </div>
            <div className="flex-1">
              <h4 className="font-medium text-gray-900 dark:text-white">
                {issue.title}
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {issue.description}
              </p>
              {issue.suggestion && (
                <div className="mt-2 p-2 bg-green-50 dark:bg-green-900/20 rounded border-l-4 border-green-400">
                  <p className="text-sm text-green-800 dark:text-green-300">
                    <strong>Suggestion:</strong> {issue.suggestion}
                  </p>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      ))}
      
      {(!analysis?.issues || analysis.issues.length === 0) && (
        <div className="card p-8 text-center">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            No Issues Found
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Your code looks good! No major issues detected.
          </p>
        </div>
      )}
    </motion.div>
  )

  const renderMetrics = () => (
    <motion.div 
      className="space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {analysis?.metrics && (
        <MetricsChart metrics={analysis.metrics} />
      )}
      
      <div className="grid grid-cols-2 gap-4">
        {analysis?.metrics && Object.entries(analysis.metrics).map(([key, value]) => (
          <div key={key} className="card p-4 text-center">
            <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {typeof value === 'number' ? value.toFixed(1) : value}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 capitalize">
              {key.replace(/([A-Z])/g, ' $1').trim()}
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )

  const renderContent = () => {
    if (isAnalyzing) return renderLoadingState()
    if (!analysis) return renderEmptyState()
    if (analysis.error) {
      return (
        <div className="card p-8 text-center">
          <XCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Analysis Failed
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            {analysis.error}
          </p>
        </div>
      )
    }

    switch (activeTab) {
      case 'summary': return renderSummary()
      case 'issues': return renderIssues()
      case 'metrics': return renderMetrics()
      default: return renderSummary()
    }
  }

  return (
    <motion.div 
      className="card p-4 flex flex-col h-full"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <div className="flex items-center space-x-4 mb-4 border-b border-gray-200 dark:border-gray-700">
        {TABS.map((tab) => {
          const Icon = tab.icon
          return (
            <motion.button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary-600 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </motion.button>
          )
        })}
      </div>

      <div className="flex-1 overflow-y-auto">
        <AnimatePresence mode="wait">
          {renderContent()}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

export default ReviewPanel