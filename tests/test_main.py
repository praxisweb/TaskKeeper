def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task_returns_201(client):
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["status"] == "todo"
    assert "id" in data
    assert "created_at" in data


def test_create_task_custom_status(client):
    response = client.post("/tasks", json={"title": "Doing this", "status": "in_progress"})
    assert response.status_code == 201
    assert response.json()["status"] == "in_progress"


def test_create_task_rejects_missing_title(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_create_task_rejects_empty_title(client):
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422


def test_create_task_rejects_blank_title(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_rejects_invalid_status(client):
    response = client.post("/tasks", json={"title": "X", "status": "flying"})
    assert response.status_code == 422


def test_get_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_get_tasks_returns_created_task(client):
    client.post("/tasks", json={"title": "My task"})
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "My task"


def test_get_tasks_oldest_first(client):
    client.post("/tasks", json={"title": "First"})
    client.post("/tasks", json={"title": "Second"})
    response = client.get("/tasks")
    data = response.json()
    assert data[0]["title"] == "First"
    assert data[1]["title"] == "Second"


def test_get_tasks_filter_by_status(client):
    client.post("/tasks", json={"title": "Todo task", "status": "todo"})
    client.post("/tasks", json={"title": "Active task", "status": "in_progress"})
    response = client.get("/tasks?status=in_progress")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Active task"


def test_get_tasks_rejects_invalid_status(client):
    response = client.get("/tasks?status=flying")
    assert response.status_code == 422


def test_frontend_route_exists(client, monkeypatch):
    import main
    from pathlib import Path
    temp_dir = main.BASE_DIR / "tests" / "temp_dir"
    temp_dir.mkdir(exist_ok=True)
    temp_index = temp_dir / "index.html"
    temp_index.write_text("<html><body>ok</body></html>")
    
    monkeypatch.setattr(main, "BASE_DIR", temp_dir)
    try:
        response = client.get("/")
        assert response.status_code == 200
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)





