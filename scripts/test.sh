#!/bin/bash

# Test script for YouTube AI Clipper
set -e

if [ -z "$1" ]; then
    echo "Usage: ./scripts/test.sh <API_ENDPOINT>"
    echo "Example: ./scripts/test.sh https://abc123.execute-api.us-east-1.amazonaws.com/Prod"
    exit 1
fi

API_ENDPOINT="$1"

echo "Testing YouTube AI Clipper API..."

# Test 1: Famous first YouTube video with "elephant" topic
echo "Test 1: First YouTube video - searching for 'elephant'"
curl -X POST \
  "${API_ENDPOINT}/analyze" \
  -H 'Content-Type: application/json' \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    "topic": "elephant"
  }' | jq '.'

echo -e "\n\n"

# Test 2: Generic video with "bitcoin" topic
echo "Test 2: Generic video - searching for 'bitcoin'"
curl -X POST \
  "${API_ENDPOINT}/analyze" \
  -H 'Content-Type: application/json' \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "topic": "bitcoin"
  }' | jq '.'

echo -e "\n\nTesting completed!"
