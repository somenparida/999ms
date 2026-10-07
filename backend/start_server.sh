#!/usr/bin/env bash
# Startup script for Member 3 Backend with multi-laptop networking helper

echo "=========================================================="
echo "🚀 Starting Autonomous Vision & Behaviour Backend Server"
echo "=========================================================="

# Display Local IP addresses
IP_ADDRESSES=$(hostname -I 2>/dev/null || ip addr show | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)

echo ""
echo "📡 YOUR LOCAL IP ADDRESS(ES):"
for ip in $IP_ADDRESSES; do
  echo "   -> http://$ip:8000"
done

echo ""
echo "🔗 WHAT TO SHARE WITH YOUR TEAMMATES:"
echo "----------------------------------------------------------"
echo "1. Swagger UI Docs: http://<YOUR_IP>:8000/docs"
echo "2. Member 1 API:    POST http://<YOUR_IP>:8000/api/videos/{video_id}/tracks/import"
echo "3. Member 2 API:    POST http://<YOUR_IP>:8000/api/videos/{video_id}/behaviours/import"
echo "4. Member 4 Base:   http://<YOUR_IP>:8000/api"
echo "----------------------------------------------------------"
echo ""

# Start uvicorn server binding to 0.0.0.0
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
