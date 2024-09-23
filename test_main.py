import os
import tempfile
import shutil
import atexit
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import SessionLocal
from app.models import Base, Picture

# create temporary directory for test database
temp_dir = tempfile.mkdtemp()
os.makedirs(temp_dir, exist_ok=True)
DATABASE_URL = f"sqlite:///{temp_dir}/test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{temp_dir}/test.db"
print(f"Test DATABASE_URL: {DATABASE_URL}")  # Debug print

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create database tables
Base.metadata.create_all(bind=engine)

# override SessionLocal with test session
app.dependency_overrides[SessionLocal] = TestingSessionLocal

client = TestClient(app)


def test_save_pictures():
    response = client.post("/save_pictures", json={"animal_type": "cat", "number_of_pictures": 1})
    assert response.status_code == 200
    assert response.json() == {"message": "1 cat pictures saved."}


def test_get_last_picture():
    client.post("/save_pictures", json={"animal_type": "dog", "number_of_pictures": 1})

    response = client.get("/get_last_picture", params={"animal_type": "dog"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"


def test_show_last_picture():
    client.post("/save_pictures", json={"animal_type": "bear", "number_of_pictures": 1})

    response = client.get("/show_last_picture", params={"animal_type": "bear"})
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "bear" in response.text.lower()


# clean up
atexit.register(lambda: shutil.rmtree(temp_dir))
