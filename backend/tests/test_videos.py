import io

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data

def test_upload_and_get_video(client):
    file_content = b"fake video bytes content"
    files = {"file": ("test_video.mp4", io.BytesIO(file_content), "video/mp4")}
    
    response = client.post("/api/videos/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["original_filename"] == "test_video.mp4"
    assert data["status"] == "uploaded"
    video_id = data["id"]

    # Get single video
    get_res = client.get(f"/api/videos/{video_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == video_id

    # List videos
    list_res = client.get("/api/videos")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

def test_delete_video(client):
    file_content = b"dummy video bytes"
    files = {"file": ("to_delete.mp4", io.BytesIO(file_content), "video/mp4")}
    upload_res = client.post("/api/videos/upload", files=files)
    video_id = upload_res.json()["id"]

    del_res = client.delete(f"/api/videos/{video_id}")
    assert del_res.status_code == 200

    get_res = client.get(f"/api/videos/{video_id}")
    assert get_res.status_code == 404
