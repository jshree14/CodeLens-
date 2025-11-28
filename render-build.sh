#!/usr/bin/env bash
# Build script for Render - installs all compilers

set -o errexit

echo "=== Installing system packages ==="

# Install Java JDK (try multiple methods)
echo "Installing Java JDK..."
apt-get update || true
apt-get install -y default-jdk || apt-get install -y openjdk-11-jdk || echo "Java installation skipped"

# Install Node.js and npm (if not already installed)
echo "Installing Node.js..."
apt-get install -y nodejs npm || echo "Node.js already installed"

# Install C++ compiler
echo "Installing g++..."
apt-get install -y g++ build-essential || echo "g++ already installed"

# Verify installations
echo "=== Verifying installations ==="
echo "Python version:"
python --version || python3 --version

echo "Java version:"
java -version 2>&1 || echo "Java not available"

echo "Node version:"
node --version || echo "Node not available"

echo "g++ version:"
g++ --version || echo "g++ not available"

echo "=== Installing Python dependencies ==="
cd backend
pip install -r requirements.txt

echo "=== Build complete ==="
