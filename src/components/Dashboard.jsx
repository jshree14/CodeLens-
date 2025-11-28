import React from 'react';
import { motion } from 'framer-motion';
import './Dashboard.css';

const Dashboard = () => {
  return (
    <motion.div
      className="dashboard glass"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <h2 className="gradient-text">Dashboard</h2>
      <p>Analytics and statistics coming soon...</p>
    </motion.div>
  );
};

export default Dashboard;