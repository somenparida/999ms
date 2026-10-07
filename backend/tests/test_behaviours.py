import io
import json
import os

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

def test_import_real_member2_behaviours_file(client):
    video_id = create_sample_video(client)

    # Check for behaviours.json at workspace root or mock dir
    paths_to_check = [
        "/home/frost/hacknex/behaviours.json",
        "./mock/behaviours.json",
        "../behaviours.json"
    ]
    file_path = None
    for p in paths_to_check:
        if os.path.exists(p):
            file_path = p
            break

    assert file_path is not None, "behaviours.json file must exist"

    with open(file_path, "r") as f:
        payload = json.load(f)

    res = client.post(f"/api/videos/{video_id}/behaviours/import", json=payload)
    assert res.status_code == 201
    behaviours = res.json()

    # 69 total behaviour records in Member 2's behaviours.json
    assert len(behaviours) == 69

    # Check tracks created
    tracks_res = client.get(f"/api/videos/{video_id}/tracks")
    assert tracks_res.status_code == 200
    tracks = tracks_res.json()
    track_ids = [t["track_id"] for t in tracks]
    assert 1 in track_ids
    assert 2 in track_ids
    assert 3 in track_ids
    assert 4 in track_ids

    # Check events auto-generated from Member 2's activity transitions
    events_res = client.get(f"/api/videos/{video_id}/events")
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) >= 4
    event_types = [e["event_type"] for e in events]
    assert "ACTIVITY_CHANGE" in event_types
