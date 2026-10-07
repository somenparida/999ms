import io

def create_sample_video(client):
    files = {"file": ("sample.mp4", io.BytesIO(b"sample video"), "video/mp4")}
    res = client.post("/api/videos/upload", files=files)
    return res.json()["id"]

def test_import_behaviours(client):
    video_id = create_sample_video(client)

    payload = {
        "behaviours": [
            {
                "track_id": 7,
                "behaviour_type": "walking",
                "start_time": 10.0,
                "end_time": 20.0,
                "confidence": 0.95,
                "classification": "normal",
                "reason": "Normal walking movement"
            }
        ]
    }

    res = client.post(f"/api/videos/{video_id}/behaviours/import", json=payload)
    assert res.status_code == 201
    behaviours = res.json()
    assert len(behaviours) == 1
    assert behaviours[0]["behaviour_type"] == "walking"

    # Get behaviours
    get_res = client.get(f"/api/videos/{video_id}/behaviours")
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1
