#!/bin/bash
set -e

show_help() {
    echo "用法: $0 {frontend|backend}"
    echo ""
    echo "說明:"
    echo "  此腳本用於 Build (建置) 並 Push (推送) Docker Image 到 GHCR。"
    echo "  會自動偵測專案中的 Version (版本)，並加上對應的 Tag。"
    echo ""
    echo "參數:"
    echo "  frontend    Build 前端 (Frontend) Image"
    echo "              Image 名稱: ghcr.io/fhsh-tp/makeup-exam-query-f4e"
    echo "              Version 來源: frontend/package.json"
    echo ""
    echo "  backend     Build 後端 (Backend) Image"
    echo "              Image 名稱: ghcr.io/fhsh-tp/makeup-exam-query-api"
    echo "              Version 來源: backend/pyproject.toml"
    echo ""
    echo "範例:"
    echo "  $0 frontend"
    echo "  $0 backend"
}

# Usage check
if [ -z "$1" ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    show_help
    exit 1
fi

# Convert to lowercase
SERVICE=$(echo "$1" | tr '[:upper:]' '[:lower:]')

# Get `.env` variable
ENV_PATH="$(cd "$(dirname "$0")/.." && pwd)/.env"

# Configure variables based on service
if [ "$SERVICE" == "frontend" ]; then
    IMAGE_NAME="ghcr.io/fhsh-tp/makeup-exam-query-system-web"
    VERSION_FILE="frontend/package.json"
    BUILD_CONTEXT="frontend"
    DOCKERFILE_OPT="" # Default Dockerfile in context
    VERSION=$(grep '"version":' "$VERSION_FILE" | cut -d '"' -f 4)
elif [ "$SERVICE" == "backend" ]; then
    IMAGE_NAME="ghcr.io/fhsh-tp/makeup-exam-query-system-api"
    VERSION_FILE="backend/pyproject.toml"
    BUILD_CONTEXT="."
    DOCKERFILE_OPT="-f backend/Dockerfile"
    VERSION=$(grep -m1 'version =' "$VERSION_FILE" | cut -d '"' -f 2)
else
    echo "Error: Invalid argument. Use 'frontend' or 'backend'."
    exit 1
fi

if [ -z "$VERSION" ]; then
    echo "Error: Could not extract version from $VERSION_FILE"
    exit 1
fi

echo "Target Service: $SERVICE"
echo "Image Name: $IMAGE_NAME"
echo "Detected version: $VERSION"

# Parse Major and Minor version
IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"

TAGS="-t $IMAGE_NAME:$VERSION -t $IMAGE_NAME:latest"

# Add Major.Minor tag
if [ -n "$MAJOR" ] && [ -n "$MINOR" ]; then
    TAGS="$TAGS -t $IMAGE_NAME:$MAJOR.$MINOR"
fi

# Add Major tag if version is >= 1.0.0
if [ "$MAJOR" -ge 1 ]; then
    TAGS="$TAGS -t $IMAGE_NAME:$MAJOR"
fi

echo "Detailed version info: Major=$MAJOR, Minor=$MINOR"
echo "Tags to be pushed: $TAGS"

# Ensure we have a builder instance that supports multi-arch
if ! docker buildx inspect mybuilder > /dev/null 2>&1; then
    docker buildx create --name mybuilder --use
fi

# Build and push
# shellcheck disable=SC2086
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --builder mybuilder \
    --provenance=false \
    $TAGS \
    $DOCKERFILE_OPT \
    --push "$BUILD_CONTEXT"

echo "Build and push for $SERVICE completed successfully."