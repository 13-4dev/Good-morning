# cython: language_level=3
# distutils: language = c++

import cython
from cython.operator cimport dereference as deref
from libc.string cimport memcpy
from cpython.ref cimport PyObject

import sys
import os
import json
from pathlib import Path
from PyQt5.QtGui import QFontDatabase, QFont, QRegion, QPainterPath, QIcon, QPixmap
from PyQt5.QtCore import Qt, QResource
import pygame
from datetime import datetime
from PIL import Image
import numpy as np
cimport numpy as np

# Constants
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

@cython.boundscheck(False)
@cython.wraparound(False)
def ensure_directories():
    cdef str user_assets = USER_ASSETS_DIR
    cdef str images_dir = os.path.join(user_assets, "images")
    cdef str audio_dir = os.path.join(user_assets, "audio")
    
    Path(user_assets).mkdir(parents=True, exist_ok=True)
    Path(images_dir).mkdir(exist_ok=True)
    Path(audio_dir).mkdir(exist_ok=True)

@cython.boundscheck(False)
@cython.wraparound(False)
def optimize_image(str image_path):
    cdef:
        int width = IMAGE_SIZE[0]
        int height = IMAGE_SIZE[1]
        int quality = IMAGE_QUALITY
        str output_path = image_path
        np.ndarray[np.uint8_t, ndim=3] img_array
    
    try:
        with Image.open(image_path) as img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Convert PIL Image to numpy array for faster processing
            img_array = np.array(img)
            
            # Resize using numpy operations
            img_resized = Image.fromarray(img_array).resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
            img_resized.save(output_path, quality=quality, optimize=True)
            
            return output_path
    except Exception as e:
        print(f"Warning: Could not optimize image: {str(e)}")
        return image_path

@cython.boundscheck(False)
@cython.wraparound(False)
def save_user_image(str image_path, str image_type):
    ensure_directories()
    
    if not os.path.exists(image_path):
        raise ValueError("Image file does not exist")
    
    cdef:
        str ext = os.path.splitext(image_path)[1]
        str new_filename
        str new_path
    
    if ext.lower() not in ['.png', '.jpg', '.jpeg']:
        raise ValueError("Invalid image format. Please use PNG or JPG.")
    
    if image_type == "character_closed":
        new_filename = "character_closed.png"
    elif image_type == "character_open":
        new_filename = "character_open.png"
    else:
        raise ValueError("Invalid image type")
    
    new_path = os.path.join(USER_ASSETS_DIR, "images", new_filename)
    os.replace(image_path, new_path) if os.path.exists(new_path) else os.rename(image_path, new_path)
    optimize_image(new_path)
    return new_path

@cython.boundscheck(False)
@cython.wraparound(False)
def get_character_images():
    cdef:
        str default_closed = os.path.join(ASSETS_DIR, "image", "cl_char.png")
        str default_open = os.path.join(ASSETS_DIR, "image", "op_char.png")
        str user_closed = os.path.join(USER_ASSETS_DIR, "images", "character_closed.png")
        str user_open = os.path.join(USER_ASSETS_DIR, "images", "character_open.png")
    
    return {
        "closed": user_closed if os.path.exists(user_closed) else default_closed,
        "open": user_open if os.path.exists(user_open) else default_open
    }

@cython.boundscheck(False)
@cython.wraparound(False)
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {
        "language": "English",
        "model": "gemma2-9b-it",
        "prompt": DEFAULT_PROMPTS["English"]
    }

@cython.boundscheck(False)
@cython.wraparound(False)
def save_config(dict config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

def initialize_pygame():
    pygame.mixer.init()

@cython.boundscheck(False)
@cython.wraparound(False)
def load_font(int font_size):
    cdef int font_id = QFontDatabase.addApplicationFont(":/fonts/PressStart2P-Regular.ttf")
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)
        if font_family:
            return QFont(font_family[0], font_size)
    
    return QFont("Consolas", font_size)

@cython.boundscheck(False)
@cython.wraparound(False)
def create_pixmap(str icon_path, int width, int height):
    return QPixmap(icon_path).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation) 