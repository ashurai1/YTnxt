#!/usr/bin/env bash
# Install ffmpeg
apt-get update && apt-get install -y ffmpeg curl unzip

# Install Deno (required by yt-dlp for YouTube signature solving)
curl -fsSL https://deno.land/install.sh | sh
export DENO_INSTALL="/opt/render/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"
echo "Deno version: $(deno --version | head -1)"

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
