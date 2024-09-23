from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_save_pictures():
    response = client.post("/save_pictures", json={"animal_type": "cat", "number_of_pictures": 1})
    assert response.status_code == 200
    assert response.json() == {"message": "1 cat pictures saved."}


def test_get_last_picture():
    response = client.get("/get_last_picture", params={"animal_type": "cat"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
