#!/bin/bash
# Auto Cookie Refresh Script for YTnxt Bot
# Runs weekly via macOS LaunchAgent

PROJECT_DIR="/Users/ashwanirai/Desktop/YTnxt/project"
LOG_FILE="$PROJECT_DIR/cookie_refresh.log"
YTDLP="$PROJECT_DIR/venv/bin/yt-dlp"

echo "=== $(date) === Refreshing YouTube cookies..." >> "$LOG_FILE"

# Export fresh cookies from Chrome
"$YTDLP" \
    --cookies-from-browser chrome \
    --cookies "$PROJECT_DIR/cookies.txt" \
    'https://www.youtube.com' \
    --skip-download \
    --no-warnings \
    >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Cookies refreshed successfully" >> "$LOG_FILE"

    # Also copy to root if it exists
    cp "$PROJECT_DIR/cookies.txt" "$(dirname "$PROJECT_DIR")/cookies.txt" 2>/dev/null

    # Git commit & push
    cd "$PROJECT_DIR"
    git add cookies.txt
    git commit -m "auto: refresh YouTube cookies - $(date '+%Y-%m-%d')" >> "$LOG_FILE" 2>&1
    git push >> "$LOG_FILE" 2>&1
    echo "✅ Pushed to GitHub — Render will redeploy automatically" >> "$LOG_FILE"
else
    echo "❌ Cookie refresh FAILED — Chrome must be open and logged in to YouTube" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
