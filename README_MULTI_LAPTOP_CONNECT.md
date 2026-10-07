# Mobile Hotspot Networking & Multi-Laptop Setup Guide

## HNX26PSI07 — Autonomous Vision & Behaviour Understanding

When all 4 team members' laptops are connected to your **Mobile Hotspot**, your backend server running on `http://0.0.0.0:8000` will handle input from **Member 1** and **Member 2**, process events & evidence, and serve API data to **Member 4's Frontend Dashboard**.

---

## 📡 Active Mobile Hotspot Configuration

Your laptop's current Mobile Hotspot IP address is:
$$\mathbf{http://10.89.105.218:8000}$$

*(Note: If you re-connect your hotspot, run `./start_server.sh` or `ip addr show wlo1` to verify the active IP).*

---

## 📲 Step-by-Step Connection Instructions for Teammates

### Step 1: Connect Teammates' Laptops to Your Mobile Hotspot Wi-Fi
- Have Member 1, Member 2, and Member 4 connect their Wi-Fi to your Mobile Hotspot.

### Step 2: Start Your Backend Server
On your laptop, run:
```bash
cd backend
./start_server.sh
```

### Step 3: Share the Specific Endpoint URLs with Each Teammate

#### 1. Share with Member 1 (Object Detection & Tracking):
- **Role**: Sends tracking bounding boxes, velocities, and 17 COCO pose keypoints.
- **Endpoint**:
  `POST http://10.89.105.218:8000/api/videos/{video_id}/tracks/import`
- **Swagger Test Link**:
  `http://10.89.105.218:8000/docs#/Tracks%20(Member%201%20Integration)/import_tracks_api_videos__video_id__tracks_import_post`

#### 2. Share with Member 2 (Behaviour Intelligence & Anomaly Detection):
- **Role**: Sends activity classifications (`STANDING`, `WALKING`, `BENDING`, `FALLING`), posture durations, and normality ratings (`NORMAL`, `POTENTIALLY_UNUSUAL`, `ABNORMAL`).
- **Endpoint**:
  `POST http://10.89.105.218:8000/api/videos/{video_id}/behaviours/import`
- **Swagger Test Link**:
  `http://10.89.105.218:8000/docs#/Behaviours%20(Member%202%20Integration)/import_behaviours_api_videos__video_id__behaviours_import_post`

#### 3. Share with Member 4 (Frontend Dashboard & Interactive UI):
- **Role**: Displays interactive dashboard, player canvas bounding boxes, live analysis progress, alert feed, evidence drawer, and timeline.
- **Base API URL**:
  `http://10.89.105.218:8000/api`
- **Frontend Prompt File**: Share [`MEMBER_4_FRONTEND_PROMPT.md`](file:///home/frost/hacknex/backend/MEMBER_4_FRONTEND_PROMPT.md) and [`README_MEMBER_4_FRONTEND.md`](file:///home/frost/hacknex/README_MEMBER_4_FRONTEND.md).

---

## 🛠️ Linux Firewall Setup (If Teammates Experience Connection Timeouts)

If your teammates are connected to your mobile hotspot but get a "Connection Refused" or timeout error, run this command in your Linux terminal to open port 8000:

```bash
sudo ufw allow 8000/tcp
```
