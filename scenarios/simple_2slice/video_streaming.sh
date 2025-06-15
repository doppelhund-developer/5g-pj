# Get the direct stream URL
VIDEO_URL="$1"
STREAM_URL=$(yt-dlp -f best -g "$VIDEO_URL")

# Check if stream URL was obtained
if [ -z "$STREAM_URL" ]; then
    echo "Failed to get stream URL."
    exit 1
fi

# Start streaming simulation using curl
echo "Streaming from: $STREAM_URL"
curl -L "$STREAM_URL" > /dev/null