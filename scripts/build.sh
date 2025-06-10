#!/bin/bash

# Build script for YouTube AI Clipper
set -e

echo "Building YouTube AI Clipper..."

# Navigate to deployment directory
cd deployment

# Build with SAM
echo "Running SAM build..."
sam build

echo "Build completed successfully!"
echo "To deploy, run: ./scripts/deploy.sh"
