#!/usr/bin/env bash
# Startup script for Member 3 Backend with Mobile Hotspot networking helper

echo "=========================================================="
echo "🚀 Starting Autonomous Vision & Behaviour Backend Server"
echo "=========================================================="

# Extract primary Wi-Fi / Mobile Hotspot IP address
WIFI_IP=$(ip -4 addr show wlo1 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' || hostname -I | awk '{print $1}')

echo ""
echo "📡 MOBILE HOTSPOT IP ADDRESS FOR TEAMMATES:"
echo "   👉 http://${WIFI_IP}:8000"
echo ""
echo "🔗 EXACT APIS TO SHARE WITH EACH TEAMMATE:"
echo "----------------------------------------------------------------------------------"
echo "1. Swagger Documentation UI: http://${WIFI_IP}:8000/docs"
echo ""
echo "2. Member 1 (Object Detection & Tracking):"
echo "   POST http://${WIFI_IP}:8000/api/videos/{video_id}/tracks/import"
echo ""
echo "3. Member 2 (Behaviour Intelligence & Anomaly Detection):"
echo "   POST http://${WIFI_IP}:8000/api/videos/{video_id}/behaviours/import"
echo ""
echo "4. Member 4 (Frontend Dashboard UI):"
echo "   Base API URL: http://${WIFI_IP}:8000/api"
echo "----------------------------------------------------------------------------------"
echo ""

# Start uvicorn server binding to 0.0.0.0 (all network interfaces)
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
