import os
import json
import io

def create_sample_video(client):
    files = {"file": ("sample.mp4", io.BytesIO(b"sample video"), "video/mp4")}
    res = client.post("/api/videos/upload", files=files)
    return res.json()["id"]

def test_import_tracks_and_positions_with_keypoints(client):
    video_id = create_sample_video(client)

    payload = {
        "tracks": [
            {
                "track_id": 7,
                "object_type": "person",
                "timestamp": 42.31,
                "detection_confidence": 0.94,
                "bbox": [100.0, 150.0, 160.0, 310.0],
                "keypoints": [
                    [130.0, 160.0, 0.95],
                    [132.0, 162.0, 0.92]
                ]
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
    assert len(positions) == 1
    assert positions[0]["timestamp"] == 42.31

def test_import_real_tracks_json_dataset(client):
    video_id = create_sample_video(client)
    tracks_json_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "../../tracks.json"))

    if os.path.exists(tracks_json_path):
        with open(tracks_json_path, "r") as f:
            tracks_payload = json.load(f)

        res = client.post(f"/api/videos/{video_id}/tracks/import", json=tracks_payload)
        assert res.status_code == 201
        tracks = res.json()
        assert len(tracks) > 0

        # Verify positions for Track #1
        pos_res = client.get(f"/api/videos/{video_id}/tracks/1/positions")
        assert pos_res.status_code == 200
        positions = pos_res.json()
        assert len(positions) > 0
        assert positions[0]["frame_number"] == 1
