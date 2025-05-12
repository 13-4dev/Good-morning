import resources_rc
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, 
                            QHBoxLayout, QLineEdit, QDialog, QComboBox, QTextEdit, 
                            QMessageBox, QCheckBox, QFileDialog)
from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtGui import QFont, QRegion, QPainterPath, QIcon
from utils_cy import (load_config, save_config, initialize_pygame, load_font, create_pixmap, 
                   DEFAULT_PROMPTS, save_user_image, get_character_images)
from generation_cy import generate_morning_message
import pygame
import sys

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = load_config()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 400, 500) 
        layout = QVBoxLayout(self)

        # Model Input
        model_label = QLabel("Model Name:", self)
        layout.addWidget(model_label)
        self.model_input = QLineEdit(self)
        self.model_input.setText(self.config.get("model", "gemma2-9b-it"))
        self.model_input.setPlaceholderText("Enter model name (e.g., gemma2-9b-it)")
        layout.addWidget(self.model_input)

        # Language Selection
        lang_label = QLabel("Select Language:", self)
        layout.addWidget(lang_label)
        self.lang_combo = QComboBox(self)
        self.lang_combo.addItems(["English", "Russian"])
        self.lang_combo.setCurrentText(self.config.get("language", "English"))
        self.lang_combo.currentTextChanged.connect(self.update_prompt)
        layout.addWidget(self.lang_combo)

        # Custom Font
        font_label = QLabel("Custom Font:", self)
        layout.addWidget(font_label)
        font_layout = QHBoxLayout()
        self.font_path = QLineEdit(self)
        self.font_path.setText(self.config.get("font_path", ""))
        self.font_path.setPlaceholderText("Path to custom font file")
        font_layout.addWidget(self.font_path)
        
        self.font_button = QPushButton("Browse", self)
        self.font_button.clicked.connect(self.browse_font)
        font_layout.addWidget(self.font_button)
        layout.addLayout(font_layout)

        # Character Images
        char_label = QLabel("Character Images:", self)
        layout.addWidget(char_label)
        
        # Closed character image
        closed_layout = QHBoxLayout()
        self.closed_char_btn = QPushButton("Upload Closed Character", self)
        self.closed_char_btn.clicked.connect(lambda: self.upload_image("character_closed"))
        closed_layout.addWidget(self.closed_char_btn)
        layout.addLayout(closed_layout)
        
        # Open character image
        open_layout = QHBoxLayout()
        self.open_char_btn = QPushButton("Upload Open Character", self)
        self.open_char_btn.clicked.connect(lambda: self.upload_image("character_open"))
        open_layout.addWidget(self.open_char_btn)
        layout.addLayout(open_layout)

        # Custom Prompt Checkbox
        self.custom_prompt_check = QCheckBox("Use Custom Prompt", self)
        self.custom_prompt_check.setChecked(bool(self.config.get("prompt")))
        layout.addWidget(self.custom_prompt_check)

        # Prompt Editing
        prompt_label = QLabel("Edit Prompt:", self)
        layout.addWidget(prompt_label)
        self.prompt_edit = QTextEdit(self)
        self.prompt_edit.setPlainText(self.config.get("prompt", DEFAULT_PROMPTS[self.lang_combo.currentText()]))
        layout.addWidget(self.prompt_edit)

        # Save Button
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

    def browse_font(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Font",
            "",
            "Font Files (*.ttf *.otf)"
        )
        if file_name:
            self.font_path.setText(file_name)

    def upload_image(self, image_type):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_name:
            try:
                if image_type == "Upload Closed Character":
                    image_type = "character_closed"
                elif image_type == "Upload Open Character":
                    image_type = "character_open"
                
                save_user_image(file_name, image_type)
                QMessageBox.information(self, "Success", "Image uploaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def update_prompt(self, language):
        if not self.custom_prompt_check.isChecked():
            self.prompt_edit.setPlainText(DEFAULT_PROMPTS[language])

    def save_settings(self):
        self.config["model"] = self.model_input.text().strip()
        self.config["language"] = self.lang_combo.currentText()
        self.config["font_path"] = self.font_path.text().strip()
        if self.custom_prompt_check.isChecked():
            self.config["prompt"] = self.prompt_edit.toPlainText()
        else:
            self.config["prompt"] = DEFAULT_PROMPTS[self.lang_combo.currentText()]
        save_config(self.config)
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        self.accept()

class ModernWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        initialize_pygame()

        if not self.config.get("token") or not self.config.get("name"):
            self.show_setup_ui()
        else:
            try:
                self.init_ui()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                self.show_setup_ui()

        pygame.mixer.music.load("data/audio/music.mp3")
        pygame.mixer.music.play(-1)

    def show_setup_ui(self):
        self.setWindowTitle("Setup")
        self.setGeometry(300, 300, 400, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)

        lang_label = QLabel("Select Language:", self)
        layout.addWidget(lang_label)
        self.lang_combo = QComboBox(self)
        self.lang_combo.addItems(["English", "Russian"])
        self.lang_combo.setCurrentText(self.config.get("language", "English"))
        layout.addWidget(self.lang_combo)

        model_label = QLabel("Model Name:", self)
        layout.addWidget(model_label)
        self.model_input = QLineEdit(self)
        self.model_input.setText(self.config.get("model", "gemma2-9b-it"))
        self.model_input.setPlaceholderText("Enter model name (e.g., gemma2-9b-it)")
        layout.addWidget(self.model_input)

        self.token_input = QLineEdit(self)
        self.token_input.setPlaceholderText("Enter API Token")
        layout.addWidget(self.token_input)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("What's your name?")
        layout.addWidget(self.name_input)

        self.custom_prompt_check = QCheckBox("Use Custom Prompt", self)
        layout.addWidget(self.custom_prompt_check)

        prompt_label = QLabel("Edit Prompt:", self)
        layout.addWidget(prompt_label)
        self.prompt_edit = QTextEdit(self)
        self.prompt_edit.setPlainText(DEFAULT_PROMPTS["English"])
        layout.addWidget(self.prompt_edit)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_setup)
        layout.addWidget(self.save_button)

        self.lang_combo.currentTextChanged.connect(self.update_prompt)

    def update_prompt(self, language):
        if not self.custom_prompt_check.isChecked():
            self.prompt_edit.setPlainText(DEFAULT_PROMPTS[language])

    def save_setup(self):
        token = self.token_input.text().strip()
        name = self.name_input.text().strip()
        model = self.model_input.text().strip()
        language = self.lang_combo.currentText()

        if not token:
            QMessageBox.warning(self, "Error", "Please enter an API token.")
            return
        if not name:
            QMessageBox.warning(self, "Error", "Please enter your name.")
            return
        if not model:
            QMessageBox.warning(self, "Error", "Please enter a model name.")
            return

        try:
            self.config["token"] = token
            self.config["name"] = name
            self.config["model"] = model
            self.config["language"] = language
            if self.custom_prompt_check.isChecked():
                self.config["prompt"] = self.prompt_edit.toPlainText()
            else:
                self.config["prompt"] = DEFAULT_PROMPTS[language]
            save_config(self.config)
            
            try:
                generate_morning_message(self.config)
                QMessageBox.information(self, "Success", "Configuration saved successfully!")
                sys.exit()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                return
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")

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

        font = load_font(16)

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

        self.settings_button = QPushButton("Settings", self)
        self.settings_button.setFont(font)
        self.settings_button.setStyleSheet(
            "background-color: #2b2b2b; "
            "color: #00ff00; "
            "border: none; "
        )
        self.settings_button.clicked.connect(self.show_settings)

        layout = QVBoxLayout(container)
        layout.addWidget(self.date_time_container, alignment=Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addWidget(self.close_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.settings_button, alignment=Qt.AlignCenter)
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

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()

    def update_text(self):
        if self.current_index < len(self.text):
            self.label.setText(self.label.text() + self.text[self.current_index])
            self.current_index += 1

            sound = pygame.mixer.Sound(r"data\audio\3.mp3")
            sound.set_volume(0.2)
            sound.play()

            self.character_window.update_character()
        else:
            self.timer.stop()

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
        
        images = get_character_images()
        self.closed_image = create_pixmap(images["closed"], 300, 300)
        self.open_image = create_pixmap(images["open"], 300, 300)
        self.character_label.setPixmap(self.closed_image)

        layout = QVBoxLayout()
        layout.addWidget(self.character_label)
        layout.setContentsMargins(0, 47, 0, 0)
        self.setLayout(layout)
         
        self.setGeometry(self.parent.geometry().x() + self.parent.width() - 300, 
                        self.parent.geometry().y() + int(self.parent.height() / 2 - 150), 
                        300, 300)
        self.show()

    def update_character(self):
        if self.parent.current_index % 2 == 0:
            self.character_label.setPixmap(self.open_image)
        else:
            self.character_label.setPixmap(self.closed_image)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernWindow()
    window.show()
    sys.exit(app.exec_())