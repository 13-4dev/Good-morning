import sys
import os
import json
from PyQt5.QtGui import QFontDatabase, QFont, QRegion, QPainterPath, QIcon, QPixmap
from PyQt5.QtCore import Qt
import pygame
from datetime import datetime

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

def initialize_pygame():
    pygame.mixer.init()

def load_font(font_path, font_size):
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        print("Ошибка: Не удалось загрузить шрифт!")
        return None
    font_family = QFontDatabase.applicationFontFamilies(font_id)
    if not font_family:
        print("Ошибка: Шрифт не содержит поддерживаемых символов!")
        return None
    return QFont(font_family[0], font_size)

def create_pixmap(icon_path, width, height):
    return QPixmap(icon_path).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)