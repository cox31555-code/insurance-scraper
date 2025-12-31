#!/bin/bash
# ============================================
# Python Cleanup Script
# ============================================
# This script removes the deprecated Python crawler files
# after successful migration to Node.js.
#
# Usage: ./cleanup-python.sh
# ============================================

set -e

echo "============================================"
echo "  Python to Node.js Migration Cleanup"
echo "============================================"
echo ""

# Check if we're in the right directory
if [ ! -f "crawler.js" ]; then
    echo "ERROR: crawler.js not found!"
    echo "Please run this script from the project root directory."
    exit 1
fi

if [ ! -f "package.json" ]; then
    echo "ERROR: package.json not found!"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Confirm before proceeding
echo "This script will remove the following Python files:"
echo ""
echo "  - crawler.py (Python crawler - replaced by crawler.js)"
echo "  - __pycache__/ (Python cache directory)"
echo ""
echo "The following files will be PRESERVED:"
echo ""
echo "  - .env (configuration)"
echo "  - public/ (frontend)"
echo "  - server.js (updated to use Node.js crawler)"
echo "  - crawler.js (new Node.js crawler)"
echo "  - package.json (updated dependencies)"
echo "  - Dockerfile (updated for Node.js)"
echo "  - README.md (documentation)"
echo "  - test/ (test suite)"
echo ""

read -p "Are you sure you want to proceed? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "Removing Python files..."

# Remove Python crawler
if [ -f "crawler.py" ]; then
    rm -f crawler.py
    echo "  ✓ Removed crawler.py"
else
    echo "  - crawler.py not found (already removed)"
fi

# Remove Python cache
if [ -d "__pycache__" ]; then
    rm -rf __pycache__
    echo "  ✓ Removed __pycache__/"
else
    echo "  - __pycache__/ not found (already removed)"
fi

# Remove any .pyc files
find . -name "*.pyc" -type f -delete 2>/dev/null && echo "  ✓ Removed .pyc files" || true

# Remove plans directory (conversion plan no longer needed)
if [ -d "plans" ]; then
    rm -rf plans
    echo "  ✓ Removed plans/ directory"
fi

echo ""
echo "============================================"
echo "  Cleanup Complete!"
echo "============================================"
echo ""
echo "The Python crawler has been removed."
echo "The project now uses the Node.js implementation."
echo ""
echo "Next steps:"
echo "  1. Run 'npm install' to install dependencies"
echo "  2. Run 'npm test' to verify the Node.js crawler"
echo "  3. Run 'npm start' to start the server"
echo ""