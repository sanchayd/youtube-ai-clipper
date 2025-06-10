#!/bin/bash

# Deploy script for YouTube AI Clipper
set -e

echo "Deploying YouTube AI Clipper..."

# Navigate to deployment directory
cd deployment

# Deploy with SAM
echo "Running SAM deploy..."
sam deploy --guided

echo "Deployment completed!"
echo "Check the outputs above for your API endpoints."
