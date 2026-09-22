#!/bin/bash
API_KEY="821bfb7d39db5d7a6ea1b5d0aa7ebd61"
HOST="www.thepittsburghwire.com"
URL="${1:-}"
if [[ "$URL" != "https://$HOST/"* ]]; then
  echo "Usage: $0 https://$HOST/<path>" >&2
  exit 1
fi
response=$(curl -sS -w '\n%{http_code}' -X POST "https://api.indexnow.org/indexnow" \
  -H "Content-Type: application/json" \
  -d "{\"host\":\"$HOST\",\"key\":\"$API_KEY\",\"keyLocation\":\"https://$HOST/$API_KEY.txt\",\"urlList\":[\"$URL\"]}") || exit 1
status="${response##*$'\n'}"
if [[ "$status" != 200 && "$status" != 202 ]]; then
  echo "IndexNow rejected $URL (HTTP $status): ${response%$'\n'*}" >&2
  exit 1
fi
echo "IndexNow accepted $URL (HTTP $status)"
