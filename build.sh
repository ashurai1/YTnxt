#!/usr/bin/env bash
# Install ffmpeg and nodejs (for yt-dlp signature decryption)
apt-get update && apt-get install -y ffmpeg nodejs

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
