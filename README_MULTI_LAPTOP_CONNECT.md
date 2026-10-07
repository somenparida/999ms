# Multi-Laptop Networking & Connection Guide

## How to Connect Teammates' Laptops to Member 3 Backend

When your team members (Member 1, Member 2, and Member 4) are working on **different laptops**, choose one of the two options below:

---

## 📡 Option A: Connected to Same Wi-Fi / Hotspot (Recommended for In-Person Hackathons)

If all 4 laptops are connected to the same Wi-Fi router or mobile hotspot:

### Step 1: Find Your Computer's Local IP Address
Run this in your terminal:
```bash
hostname -I
```
Look for your IP address (e.g., `192.168.1.50` or `10.89.105.218`).

### Step 2: Start Your Backend Server
Run:
```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
*(The `--host 0.0.0.0` flag tells Uvicorn to listen on all network interfaces so other laptops can reach it!)*

### Step 3: Tell Teammates to Replace `localhost` with Your IP Address:

- **Interactive Swagger Docs**: `http://<YOUR_IP>:8000/docs`
- **Member 1 (Object Detection & Tracking)**:
  `POST http://<YOUR_IP>:8000/api/videos/{video_id}/tracks/import`
- **Member 2 (Behaviour Analysis)**:
  `POST http://<YOUR_IP>:8000/api/videos/{video_id}/behaviours/import`
- **Member 4 (Frontend Dashboard)**:
  Set API Base URL in React/Next.js to `http://<YOUR_IP>:8000/api`

---

## 🌐 Option B: Different Wi-Fi / Remote Networks (Using Free Tunneling)

If teammates are at home or on different Wi-Fi networks, use **ngrok** or **localtunnel** to expose your local backend securely to the internet.

### Using `ngrok` (Free):
1. Install ngrok or run:
   ```bash
   npx ngrok http 8000
   ```
2. ngrok will generate a public HTTPS URL (e.g. `https://xxxx.ngrok-free.app`).
3. Teammates anywhere in the world can hit:
   - **Member 1**: `POST https://xxxx.ngrok-free.app/api/videos/{video_id}/tracks/import`
   - **Member 2**: `POST https://xxxx.ngrok-free.app/api/videos/{video_id}/behaviours/import`
   - **Member 4**: Base URL `https://xxxx.ngrok-free.app/api`
   - **Swagger Docs**: `https://xxxx.ngrok-free.app/docs`

---

## 🔒 Firewall Troubleshooting (If Teammates Get "Connection Refused")

If teammates on the same Wi-Fi get a connection timeout error, your Linux firewall (`ufw`) might be blocking port 8000.

To allow incoming connections on port 8000:
```bash
sudo ufw allow 8000/tcp
```
