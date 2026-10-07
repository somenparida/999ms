import io

def create_sample_video(client):
    files = {"file": ("sample.mp4", io.BytesIO(b"sample video"), "video/mp4")}
    res = client.post("/api/videos/upload", files=files)
    return res.json()["id"]

def test_import_tracks_and_positions(client):
    video_id = create_sample_video(client)

    payload = {
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
                "timestamp": 45.00,
                "frame_number": 1350,
                "bbox": [125, 82, 220, 350],
                "center": [175, 217],
                "confidence": 0.95
            }
        ]
    }

    res = client.post(f"/api/videos/{video_id}/tracks/import", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert len(data) == 1
    assert data[0]["track_id"] == 7

    # Get tracks list
    tracks_res = client.get(f"/api/videos/{video_id}/tracks")
    assert tracks_res.status_code == 200
    assert len(tracks_res.json()) == 1

    # Get positions
    pos_res = client.get(f"/api/videos/{video_id}/tracks/7/positions")
    assert pos_res.status_code == 200
    positions = pos_res.json()
    assert len(positions) == 2
    assert positions[0]["frame_number"] == 1269
