# Get the direct stream URL
: '
VIDEO_URL="$1"
STREAM_URL=$(yt-dlp -f best -g "$VIDEO_URL")

# Check if stream URL was obtained
if [ -z "$STREAM_URL" ]; then
    echo "Failed to get stream URL."
    exit 1
fi

# Start streaming simulation using curl
while true; do
    echo "Streaming from: $STREAM_URL"
    curl -L "$STREAM_URL" > /dev/null
    sleep 2
done
'

#TODO add some fancy shit
#only temp test
curl -L --interface uesimtun0 -o /dev/null https://github.com/KiCad/kicad-source-mirror/releases/download/9.0.3/kicad-9.0.3-x86_64.exe