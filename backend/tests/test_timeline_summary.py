import io

def create_sample_video(client):
    files = {"file": ("sample.mp4", io.BytesIO(b"sample video"), "video/mp4")}
    res = client.post("/api/videos/upload", files=files)
    return res.json()["id"]

def test_timeline_and_summary_endpoints(client):
    video_id = create_sample_video(client)

    # Add tracks
    client.post(f"/api/videos/{video_id}/tracks/import", json={
        "tracks": [
            {
                "track_id": 1,
                "object_type": "person",
                "timestamp": 5.0,
                "frame_number": 150,
                "bbox": [100, 100, 50, 100],
                "confidence": 0.90
            }
        ]
    })

    # Add normal & abnormal behaviours
    client.post(f"/api/videos/{video_id}/behaviours/import", json={
        "behaviours": [
            {
                "track_id": 1,
                "behaviour_type": "walking",
                "start_time": 5.0,
                "end_time": 10.0,
                "confidence": 0.95,
                "classification": "normal"
            },
            {
                "track_id": 1,
                "behaviour_type": "restricted_area_entry",
                "start_time": 15.0,
                "end_time": 25.0,
                "confidence": 0.93,
                "classification": "abnormal",
                "reason": "Person entered restricted zone"
            }
        ]
    })

    # Timeline check
    timeline_res = client.get(f"/api/videos/{video_id}/timeline")
    assert timeline_res.status_code == 200
    timeline = timeline_res.json()
    assert len(timeline) == 2
    assert timeline[0]["type"] == "walking"
    assert timeline[1]["type"] == "restricted_area_entry"

    # Summary check
    summary_res = client.get(f"/api/videos/{video_id}/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["unique_tracks"] == 1
    assert summary["normal_events"] == 1
    assert summary["abnormal_events"] == 1
    assert summary["high_risk_events"] == 1
