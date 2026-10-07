import io

def create_sample_video(client):
    files = {"file": ("sample.mp4", io.BytesIO(b"sample video"), "video/mp4")}
    res = client.post("/api/videos/upload", files=files)
    return res.json()["id"]

def test_abnormal_behaviour_generates_event_and_evidence(client):
    video_id = create_sample_video(client)

    # Import track first
    track_payload = {
        "tracks": [
            {
                "track_id": 7,
                "object_type": "person",
                "timestamp": 42.31,
                "frame_number": 1269,
                "bbox": [120, 80, 220, 350],
                "center": [170, 215],
                "confidence": 0.94
            }
        ]
    }
    client.post(f"/api/videos/{video_id}/tracks/import", json=track_payload)

    # Import abnormal behaviour
    behaviour_payload = {
        "behaviours": [
            {
                "track_id": 7,
                "behaviour_type": "restricted_area_entry",
                "start_time": 42.31,
                "end_time": 55.82,
                "confidence": 0.94,
                "classification": "abnormal",
                "reason": "Person entered restricted zone."
            }
        ]
    }

    b_res = client.post(f"/api/videos/{video_id}/behaviours/import", json=behaviour_payload)
    assert b_res.status_code == 201

    # Verify event was generated
    events_res = client.get(f"/api/videos/{video_id}/events")
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) == 1
    event = events[0]
    assert event["event_type"] == "restricted_area_entry"
    assert event["severity"] == "high"
    assert event["status"] == "detected"

    # Test patch event status
    patch_res = client.patch(f"/api/events/{event['id']}", json={"status": "confirmed"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "confirmed"

    # Verify evidence items attached
    evidence_res = client.get(f"/api/events/{event['id']}/evidence")
    assert evidence_res.status_code == 200
    evidence_items = evidence_res.json()
    assert len(evidence_items) >= 1
