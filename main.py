from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtGui import QFont, QRegion, QPainterPath, QIcon
from utils import load_config, save_config, initialize_pygame, load_font, create_pixmap
from generation import generate_morning_message
import pygame
import sys

class ModernWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        initialize_pygame()

        if not self.config.get("token") or not self.config.get("name"):
            self.show_setup_ui()
        else:
            self.init_ui()

        pygame.mixer.music.load("data/audio/music.mp3")
        pygame.mixer.music.play(-1)  # 

    def show_setup_ui(self):
        self.setWindowTitle("Setup")
        self.setGeometry(300, 300, 400, 200)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)

        self.token_input = QLineEdit(self)
        self.token_input.setPlaceholderText("Введите токен")
        layout.addWidget(self.token_input)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Как вас зовут?")
        layout.addWidget(self.name_input)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.save_setup)
        layout.addWidget(self.save_button)

        self.save_button.clicked.connect(self.close)  # Закрываем окно после сохранения настроек

    def save_setup(self):
        token = self.token_input.text().strip()
        name = self.name_input.text().strip()

        if token and name:
            self.config["token"] = token
            self.config["name"] = name
            save_config(self.config)
            sys.exit()  # Выходим из программы после сохранения настроек

    def init_ui(self):
        self.setWindowTitle("GoodMorning")
        self.setWindowIcon(QIcon("fumo.ico"))
        self.setGeometry(0, 0, 800, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.setGeometry(x, y, 800, 400)

        path = QPainterPath()
        path.addRoundedRect(0, 0, 800, 400, 30, 30)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

        container = QWidget(self)
        container.setGeometry(0, 0, 800, 400)
        container.setStyleSheet(
            "background-color: #2b2b2b; "
            "border-radius: 30px; "
        )

        font = load_font("PressStart2P-Regular.ttf", 16)

        self.date_time_container = QWidget(self)
        self.date_time_layout = QHBoxLayout(self.date_time_container)
        self.date_time_layout.setContentsMargins(0, 0, 0, 0)
        self.date_time_container.setStyleSheet("background-color: transparent;")

        self.date_time_label = QLabel("", self)
        small_font = QFont(font)
        small_font.setPointSize(12)
        self.date_time_label.setFont(small_font)
        self.date_time_label.setStyleSheet("color: #888888;")

        self.time_icon = QLabel(self)
        self.time_icon.setFixedSize(20, 20)
        self.time_icon.setStyleSheet("background-color: transparent;")

        self.date_time_layout.addWidget(self.time_icon)
        self.date_time_layout.addWidget(self.date_time_label)
        self.date_time_layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel("", self)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("color: #ffffff;")

        self.close_button = QPushButton("txh", self)
        self.close_button.setFont(font)
        self.close_button.setStyleSheet(
            "background-color: #2b2b2b; "
            "color: #00ff00; "
            "border: none; "
        )
        self.close_button.clicked.connect(self.close)

        layout = QVBoxLayout(container)
        layout.addWidget(self.date_time_container, alignment=Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addWidget(self.close_button, alignment=Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)

        self.text = generate_morning_message(self.config)
        self.current_index = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_text)
        self.timer.start(50)

        self.date_time_timer = QTimer(self)
        self.date_time_timer.timeout.connect(self.update_date_time)
        self.date_time_timer.start(1000)
        self.update_date_time()

        self.character_window = CharacterWindow(self)

    def update_text(self):
        if self.current_index < len(self.text):
            self.label.setText(self.label.text() + self.text[self.current_index])
            self.current_index += 1

            # Проигрываем звук только для текущего символа
            sound = pygame.mixer.Sound(r"data\audio\3.mp3")
            sound.set_volume(0.2)
            sound.play()

            # Обновляем персонажа в отдельном окне
            self.character_window.update_character()
        else:
            self.timer.stop()

            # Останавливаем все звуки
            pygame.mixer.stop()


    def update_date_time(self):
        current_time = QDateTime.currentDateTime()
        time_str = current_time.toString("dddd, MMMM d yyyy, hh:mm:ss AP")
        self.date_time_label.setText(time_str)

        hour = current_time.time().hour()
        if 5 <= hour < 12:
            icon_path = "data/image/sunrise.png"
        elif 12 <= hour < 18:
            icon_path = "data/image/sun.png"
        else:
            icon_path = "data/image/moon.png"

        pixmap = create_pixmap(icon_path, 20, 20)
        self.time_icon.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'character_window'):
            self.character_window.setGeometry(self.geometry().x() + self.width() - 80, self.geometry().y() + int(self.height() / 2 - 150), 300, 300)

class CharacterWindow(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.character_label = QLabel(self)
        self.character_label.setFixedSize(300, 300)  
        self.character_label.setPixmap(create_pixmap("data/image/cl_char.png", 300, 300))  

        layout = QVBoxLayout()
        layout.addWidget(self.character_label)
        layout.setContentsMargins(0, 47, 0, 0)
        self.setLayout(layout)
         
        self.setGeometry(self.parent.geometry().x() + self.parent.width() - 300, self.parent.geometry().y() + int(self.parent.height() / 2 - 150), 300, 300)
        self.show()

    def update_character(self):
        if self.parent.current_index % 2 == 0:
            self.character_label.setPixmap(create_pixmap("data/image/op_char.png", 300, 300))  
        else:
            self.character_label.setPixmap(create_pixmap("data/image/cl_char.png", 300, 300))  

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernWindow()
    window.show()
    sys.exit(app.exec_())