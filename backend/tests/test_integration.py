import io

def test_full_end_to_end_integration_flow(client):
    """
    Complete End-to-End Integration Test matching README section 30 requirements:
    1. Upload Video & Create Video Record
    2. Start Analysis Job
    3. Import Track Data (Member 1 Integration)
    4. Import Behaviour Data (Member 2 Integration)
    5. Detect Abnormal Behaviour & Auto-Generate Event
    6. Attach Evidence
    7. Retrieve API results for Dashboard (Member 4 Integration)
    """
    # 1. Upload Video
    video_bytes = b"dummy mp4 data stream for testing"
    files = {"file": ("surveillance_hallway.mp4", io.BytesIO(video_bytes), "video/mp4")}
    upload_res = client.post("/api/videos/upload", files=files)
    assert upload_res.status_code == 201
    video_data = upload_res.json()
    video_id = video_data["id"]

    # 2. Start Analysis Job
    job_res = client.post(f"/api/videos/{video_id}/analyze")
    assert job_res.status_code == 200
    assert job_res.json()["status"] == "processing"

    # 3. Member 1 Integration: Track Data Import
    track_import_payload = {
        "tracks": [
            {
                "track_id": 7,
                "object_type": "person",
                "timestamp": 42.31,
                "frame_number": 1269,
                "bbox": [120, 80, 220, 350],
                "center": [170, 215],
                "confidence": 0.94
            },
            {
                "track_id": 7,
                "object_type": "person",
                "timestamp": 55.82,
                "frame_number": 1674,
                "bbox": [150, 90, 220, 350],
                "center": [200, 225],
                "confidence": 0.95
            }
        ]
    }
    t_res = client.post(f"/api/videos/{video_id}/tracks/import", json=track_import_payload)
    assert t_res.status_code == 201

    # Verify track positions stored
    pos_res = client.get(f"/api/videos/{video_id}/tracks/7/positions")
    assert pos_res.status_code == 200
    assert len(pos_res.json()) == 2

    # 4. Member 2 Integration: Behaviour Data Import
    behaviour_import_payload = {
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
    b_res = client.post(f"/api/videos/{video_id}/behaviours/import", json=behaviour_import_payload)
    assert b_res.status_code == 201

    # 5 & 6. Verify Event Generation & Evidence Attachment
    events_res = client.get(f"/api/videos/{video_id}/events")
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) == 1
    event = events[0]
    assert event["event_type"] == "restricted_area_entry"
    assert event["severity"] == "high"
    event_id = event["id"]

    evidence_res = client.get(f"/api/events/{event_id}/evidence")
    assert evidence_res.status_code == 200
    evidence_list = evidence_res.json()
    assert len(evidence_list) >= 1

    # 7. Member 4 Integration: Timeline & Summary Retrieval
    timeline_res = client.get(f"/api/videos/{video_id}/timeline")
    assert timeline_res.status_code == 200
    timeline = timeline_res.json()
    assert len(timeline) >= 1
    assert timeline[0]["type"] == "restricted_area_entry"

    summary_res = client.get(f"/api/videos/{video_id}/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["unique_tracks"] == 1
    assert summary["abnormal_events"] == 1
    assert summary["high_risk_events"] == 1
