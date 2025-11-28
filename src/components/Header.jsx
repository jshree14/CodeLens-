import React from 'react';
import { motion } from 'framer-motion';
import { Code2, BarChart3, FileCode } from 'lucide-react';
import './Header.css';

const Header = ({ currentView, setCurrentView, mousePosition }) => {
  const navItems = [
    { id: 'editor', label: 'Code Analyzer', icon: Code2 },
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
  ];

  return (
    <motion.header
      className="header glass"
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, type: 'spring' }}
    >
      <div className="header-content">
        {/* Logo */}
        <motion.div
          className="logo"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <div className="logo-icon">
            <Code2 size={32} />
          </div>
          <div className="logo-text">
            <h1 className="gradient-text">CodeLens AI</h1>
            <p className="logo-subtitle">Intelligent Code Review</p>
          </div>
        </motion.div>

        {/* Navigation */}
        <nav className="nav">
          {navItems.map((item, index) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;

            return (
              <motion.button
                key={item.id}
                className={`nav-item ${isActive ? 'active' : ''}`}
                onClick={() => setCurrentView(item.id)}
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Icon size={20} />
                <span>{item.label}</span>
                {isActive && (
                  <motion.div
                    className="active-indicator"
                    layoutId="activeTab"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}
              </motion.button>
            );
          })}
        </nav>

        {/* Status Indicator */}
        <motion.div
          className="status-indicator"
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5 }}
        >
          <div className="status-dot pulse" />
          <span>API Connected</span>
        </motion.div>
      </div>

      {/* Animated underline */}
      <motion.div
        className="header-glow"
        animate={{
          x: mousePosition.x * 0.01,
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          opacity: { duration: 2, repeat: Infinity },
          x: { type: 'spring', stiffness: 50 },
        }}
      />
    </motion.header>
  );
};

export default Header;