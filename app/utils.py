import random
import requests


def get_random_cat_image():
    response = requests.get("https://api.thecatapi.com/v1/images/search")
    data = response.json()
    image_url = data[0]["url"]
    return image_url


def get_random_dog_image():
    width = random.randint(200, 500)
    height = random.randint(200, 500)
    image_url = f"https://place.dog/{width}/{height}"
    return image_url


def get_random_bear_image():
    width = random.randint(200, 500)
    height = random.randint(200, 500)
    image_url = f"https://placebear.com/{width}/{height}"
    return image_url


def download_image(url):
    response = requests.get(url)
    return response.content
