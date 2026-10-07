import io

def create_sample_video(client):
    files = {"file": ("sample.mp4", io.BytesIO(b"sample video"), "video/mp4")}
    res = client.post("/api/videos/upload", files=files)
    return res.json()["id"]

def test_import_behaviours_member2_format(client):
    video_id = create_sample_video(client)

    payload = {
        "behaviours": [
            {
                "track_id": 7,
                "activity": "BENDING",
                "status": "POTENTIALLY_UNUSUAL",
                "severity": "LOW",
                "timestamp": 42.0,
                "duration": 35.0,
                "confidence": 0.95,
                "previous_activity": "WALKING",
                "reason": ["Prolonged bending", "repetitive posture risk"]
            },
            {
                "track_id": 7,
                "activity": "FALLING",
                "status": "ABNORMAL",
                "severity": "HIGH",
                "timestamp": 80.0,
                "duration": 0.0,
                "confidence": 0.94,
                "reason": ["rapid downward movement", "posture collapse"],
                "event": {
                    "type": "POSSIBLE_FALL",
                    "severity": "HIGH",
                    "details": {"max_velocity": 60.0, "fall_score": 0.94}
                }
            }
        ]
    }

    res = client.post(f"/api/videos/{video_id}/behaviours/import", json=payload)
    assert res.status_code == 201
    behaviours = res.json()
    assert len(behaviours) == 2
    assert behaviours[0]["behaviour_type"] == "BENDING"
    assert behaviours[1]["behaviour_type"] == "FALLING"

    # Get events triggered by abnormal behaviour
    events_res = client.get(f"/api/videos/{video_id}/events")
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) == 2
    event_types = [e["event_type"] for e in events]
    assert "POSSIBLE_FALL" in event_types or "FALLING" in event_types
    assert "BENDING" in event_types
