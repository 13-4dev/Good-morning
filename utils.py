import sys
import os
import json
import shutil
from pathlib import Path
from PyQt5.QtGui import QFontDatabase, QFont, QRegion, QPainterPath, QIcon, QPixmap
from PyQt5.QtCore import Qt, QResource
import pygame
from datetime import datetime
from PIL import Image

CONFIG_FILE = "config.json"
ASSETS_DIR = "data"
USER_ASSETS_DIR = "data/user"

IMAGE_SIZE = (300, 300)
IMAGE_QUALITY = 85  

DEFAULT_PROMPTS = {
    "English": """
    Generate a single-line morning wish that encourages the person to: take care of themselves, their appearance, their well-being, complete tasks, brush their teeth, and go to bed on time.
    Name: {name}
    Date: {day}
    Time: {time}
    """,
    "Russian": """
    Сгенерируй в одну строку пожелания на доброе утро, так же человек должен: заботиться о себе, о внешности, о состоянии, выполнять задачи, чистить зубы и засыпать вовремя.
    Имя: {name}
    Дата: {day}
    Время: {time}
    """
}

def ensure_directories():
    Path(USER_ASSETS_DIR).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(USER_ASSETS_DIR, "images")).mkdir(exist_ok=True)
    Path(os.path.join(USER_ASSETS_DIR, "audio")).mkdir(exist_ok=True)

def optimize_image(image_path):
    try:
        with Image.open(image_path) as img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            img = img.resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
            
            output_path = image_path
            img.save(output_path, quality=IMAGE_QUALITY, optimize=True)
            return output_path
    except Exception as e:
        print(f"Warning: Could not optimize image: {str(e)}")
        return image_path

def save_user_image(image_path, image_type):
    ensure_directories()
    
    if not os.path.exists(image_path):
        raise ValueError("Image file does not exist")
    
    ext = os.path.splitext(image_path)[1]
    if ext.lower() not in ['.png', '.jpg', '.jpeg']:
        raise ValueError("Invalid image format. Please use PNG or JPG.")
    
    if image_type == "character_closed":
        new_filename = "character_closed.png"
    elif image_type == "character_open":
        new_filename = "character_open.png"
    else:
        raise ValueError("Invalid image type")
    
    new_path = os.path.join(USER_ASSETS_DIR, "images", new_filename)
    shutil.copy2(image_path, new_path)
    optimize_image(new_path)
    return new_path

def get_character_images():
    default_closed = os.path.join(ASSETS_DIR, "image", "cl_char.png")
    default_open = os.path.join(ASSETS_DIR, "image", "op_char.png")
    
    user_closed = os.path.join(USER_ASSETS_DIR, "images", "character_closed.png")
    user_open = os.path.join(USER_ASSETS_DIR, "images", "character_open.png")
    
    return {
        "closed": user_closed if os.path.exists(user_closed) else default_closed,
        "open": user_open if os.path.exists(user_open) else default_open
    }

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {
        "language": "English",
        "model": "gemma2-9b-it",
        "prompt": DEFAULT_PROMPTS["English"]
    }

def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

def initialize_pygame():
    pygame.mixer.init()

def load_font(font_size):
    font_id = QFontDatabase.addApplicationFont(":/fonts/PressStart2P-Regular.ttf")
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)
        if font_family:
            return QFont(font_family[0], font_size)
    
   
    return QFont("Consolas", font_size)

def create_pixmap(icon_path, width, height):
    return QPixmap(icon_path).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)