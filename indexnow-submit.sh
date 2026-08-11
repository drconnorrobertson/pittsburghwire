#!/bin/bash
API_KEY="821bfb7d39db5d7a6ea1b5d0aa7ebd61"
HOST="www.thepittsburghwire.com"
URL="$1"
if [ -z "$URL" ]; then echo "Usage: $0 <url>"; exit 1; fi
curl -s -X POST "https://api.indexnow.org/indexnow" \
  -H "Content-Type: application/json" \
  -d "{\"host\":\"$HOST\",\"key\":\"$API_KEY\",\"keyLocation\":\"https://$HOST/$API_KEY.txt\",\"urlList\":[\"$URL\"]}"
echo "Submitted $URL to IndexNow"
