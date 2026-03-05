#!/usr/bin/env bash

set -e

REPO="yamlr/yamlr"
INSTALL_DIR="/usr/local/bin"
BIN_NAME="yamlr"

echo "Downloading latest Yamlr release..."

# Get latest release tag
API_URL="https://api.github.com/repos/$REPO/releases/latest"
LATEST_TAG=$(curl -sL $API_URL | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$LATEST_TAG" ]; then
    echo "Error: Could not determine latest release tag."
    exit 1
fi

echo "Latest tag: $LATEST_TAG"

# Determine OS and Arch
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then ARCH="amd64"; fi
if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then ARCH="arm64"; fi

# Current Nuitka matrix maps everything to amd64/x86_64 for simplicity, but script handles logic
FILE_NAME="yamlr-${LATEST_TAG}-${OS}-amd64.tar.gz"
DOWNLOAD_URL="https://github.com/$REPO/releases/download/$LATEST_TAG/$FILE_NAME"

echo "Downloading $DOWNLOAD_URL ..."
curl -fsSL -o "/tmp/$FILE_NAME" "$DOWNLOAD_URL"

echo "Extracting telemetry..."
tar -xzf "/tmp/$FILE_NAME" -C "/tmp"

echo "Installing to $INSTALL_DIR (requires sudo)..."
sudo mv "/tmp/$BIN_NAME" "$INSTALL_DIR/$BIN_NAME"
sudo chmod +x "$INSTALL_DIR/$BIN_NAME"

# Cleanup
rm -f "/tmp/$FILE_NAME"

echo ""
echo "✅ Yamlr Installed Successfully!"
echo "Run 'yamlr welcome' to get started."
