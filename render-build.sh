#!/usr/bin/env bash
# Build script for Render - installs all compilers

set -o errexit

echo "=== Installing system packages ==="

# Update package list
apt-get update

# Install Java JDK
echo "Installing Java JDK..."
apt-get install -y default-jdk

# Install Node.js and npm (if not already installed)
echo "Installing Node.js..."
apt-get install -y nodejs npm

# Install C++ compiler
echo "Installing g++..."
apt-get install -y g++ build-essential

# Verify installations
echo "=== Verifying installations ==="
echo "Python version:"
python --version

echo "Java version:"
java -version

echo "Node version:"
node --version

echo "g++ version:"
g++ --version

echo "=== Installing Python dependencies ==="
cd backend
pip install -r requirements.txt

echo "=== Build complete ==="
