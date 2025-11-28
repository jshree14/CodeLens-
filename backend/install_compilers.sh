#!/bin/bash
# Install compilers for code execution on Render

echo "Installing compilers..."

# Install Java JDK
echo "Installing Java JDK..."
apt-get update
apt-get install -y default-jdk || echo "Java installation failed (may need root)"

# Install Node.js (usually pre-installed on Render)
echo "Checking Node.js..."
node --version || echo "Node.js not available"

# Install g++ for C/C++
echo "Installing g++..."
apt-get install -y g++ build-essential || echo "g++ installation failed (may need root)"

# Verify installations
echo "Verifying installations..."
echo "Java version:"
java -version 2>&1 || echo "Java not installed"
echo "Node version:"
node --version 2>&1 || echo "Node not installed"
echo "g++ version:"
g++ --version 2>&1 || echo "g++ not installed"

echo "Compiler installation complete!"
