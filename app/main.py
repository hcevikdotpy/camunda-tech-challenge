from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import uuid
from app import db
from app.models import SavePicturesRequest, Picture, Base
from app.utils import (
    get_random_cat_image,
    get_random_dog_image,
    get_random_bear_image,
    download_image,
)

# project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# directories for images and templates
IMAGES_DIR = os.path.join(BASE_DIR, "images")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app = FastAPI()

# mount static files
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.post("/save_pictures")
def save_pictures(request: SavePicturesRequest):
    animal_type = request.animal_type.lower()
    number = request.number_of_pictures

    if animal_type not in ["cat", "dog", "bear"]:
        raise HTTPException(status_code=400, detail="Invalid animal type")

    session = db.SessionLocal()

    for _ in range(number):
        try:
            if animal_type == "cat":
                image_url = get_random_cat_image()
            elif animal_type == "dog":
                image_url = get_random_dog_image()
            elif animal_type == "bear":
                image_url = get_random_bear_image()

            image_content = download_image(image_url)
            file_name = f"{uuid.uuid4()}.jpg"
            file_path = os.path.join(IMAGES_DIR, file_name)
            os.makedirs(IMAGES_DIR, exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(image_content)

            picture = Picture(animal_type=animal_type, file_path=file_path)
            session.add(picture)
            session.commit()

        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    session.close()
    return {"message": f"{number} {animal_type} pictures saved."}


@app.get("/get_last_picture")
def get_last_picture(animal_type: str):
    animal_type = animal_type.lower()
    if animal_type not in ["cat", "dog", "bear"]:
        raise HTTPException(status_code=400, detail="Invalid animal type")

    session = db.SessionLocal()
    picture = (
        session.query(Picture)
        .filter(Picture.animal_type == animal_type)
        .order_by(Picture.timestamp.desc())
        .first()
    )
    session.close()

    if not picture:
        raise HTTPException(status_code=404, detail="No picture found for this animal type")

    return FileResponse(
        path=picture.file_path,
        media_type="image/jpeg",
        filename=os.path.basename(picture.file_path),
    )


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/show_last_picture", response_class=HTMLResponse)
def show_last_picture(request: Request, animal_type: str = Query(default="cat")):
    print(f"Received request for animal_type: {animal_type}")  # debug print
    animal_type = animal_type.lower()
    if animal_type not in ["cat", "dog", "bear"]:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "Invalid animal type"}
        )

    session = db.SessionLocal()
    picture = (
        session.query(Picture)
        .filter(Picture.animal_type == animal_type)
        .order_by(Picture.timestamp.desc())
        .first()
    )
    session.close()

    if not picture:
        print(f"No picture found for animal_type: {animal_type}")  # debug print
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "No picture found"}
        )

    print(f"Found picture: {picture.file_path}")  # debug print
    image_url = f"/images/{os.path.basename(picture.file_path)}"
    return templates.TemplateResponse(
        "show_picture.html",
        {"request": request, "image_url": image_url, "animal_type": animal_type},
    )
