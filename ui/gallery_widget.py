import os
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QScrollArea, QFileDialog, QMessageBox, QDialog,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from database import IMAGES_DIR
from ui.styles import COLORS

COLS = 5
THUMB = 110


class ThumbnailCard(QFrame):
    clicked = pyqtSignal(int)
    delete_req = pyqtSignal(int)

    def __init__(self, image_id: int, full_path: str, is_cover: bool, parent=None):
        super().__init__(parent)
        self.image_id = image_id
        self._selected = False

        self.setFixedSize(THUMB, THUMB)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

        img_label = QLabel(self)
        img_label.setGeometry(0, 0, THUMB, THUMB)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_pixmap(img_label, full_path)

        self._star = QLabel("★", self)
        self._star.setGeometry(4, 4, 22, 22)
        self._star.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._star.setStyleSheet(
            f"color:{COLORS['gold']}; font-size:13px;"
            "background:rgba(255,255,255,0.85); border-radius:11px;"
        )
        self._star.setVisible(is_cover)

        del_btn = QPushButton("×", self)
        del_btn.setGeometry(THUMB - 26, 4, 22, 22)
        del_btn.setStyleSheet(
            "QPushButton{background:rgba(26,24,21,0.65);color:white;border:none;"
            "border-radius:11px;font-size:14px;font-weight:bold;}"
            "QPushButton:hover{background:rgba(139,32,32,0.9);}"
        )
        del_btn.clicked.connect(lambda: self.delete_req.emit(self.image_id))

    @staticmethod
    def _load_pixmap(label: QLabel, path: str):
        if os.path.exists(path):
            px = QPixmap(path)
            if not px.isNull():
                scaled = px.scaled(
                    THUMB, THUMB,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                x = (scaled.width() - THUMB) // 2
                y = (scaled.height() - THUMB) // 2
                label.setPixmap(scaled.copy(x, y, THUMB, THUMB))
                return
        label.setText("?")
        label.setStyleSheet(f"background:{COLORS['paper_2']};color:{COLORS['ink_3']};font-size:22px;")

    def _apply_style(self):
        border = COLORS['gold'] if self._selected else COLORS['paper_3']
        self.setStyleSheet(
            f"ThumbnailCard{{border:2px solid {border};border-radius:6px;"
            f"background:{COLORS['paper_2']};}}"
        )

    def set_selected(self, selected: bool):
        self._selected = selected
        self._apply_style()

    def set_cover(self, is_cover: bool):
        self._star.setVisible(is_cover)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.image_id)
        super().mousePressEvent(event)


class ImageViewerDialog(QDialog):
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Photo")
        self.setMinimumSize(500, 420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        scroll = QScrollArea()
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setStyleSheet(f"border:1px solid {COLORS['paper_3']};border-radius:4px;")

        img_label = QLabel()
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        px = QPixmap(image_path)
        if not px.isNull():
            screen = self.screen()
            max_w = int(screen.availableGeometry().width() * 0.8) if screen else 900
            max_h = int(screen.availableGeometry().height() * 0.8) if screen else 700
            if px.width() > max_w or px.height() > max_h:
                px = px.scaled(max_w, max_h, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        img_label.setPixmap(px)
        scroll.setWidget(img_label)
        layout.addWidget(scroll, 1)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, 0, Qt.AlignmentFlag.AlignRight)


class GalleryWidget(QWidget):
    def __init__(self, db, watch_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.watch_id = watch_id
        self._selected_id = None
        self._cards: dict[int, ThumbnailCard] = {}
        self._build_ui()
        if self.watch_id is not None:
            self._load_images()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        self._unsaved_msg = QLabel("Save the watch first to add photos.")
        self._unsaved_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._unsaved_msg.setStyleSheet(f"color:{COLORS['ink_3']};font-style:italic;font-size:13px;")
        root.addWidget(self._unsaved_msg)

        self._gallery_area = QWidget()
        ga_layout = QVBoxLayout(self._gallery_area)
        ga_layout.setContentsMargins(0, 0, 0, 0)
        ga_layout.setSpacing(10)

        # Scroll area containing the grid
        scroll = QScrollArea()
        scroll.setMinimumHeight(240)
        scroll.setStyleSheet(
            f"QScrollArea{{border:1px solid {COLORS['paper_3']};border-radius:6px;"
            f"background:{COLORS['white']};}}"
        )

        self._grid_widget = QWidget()
        self._grid_widget.setStyleSheet(f"background:{COLORS['white']};")
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(8)
        self._grid.setContentsMargins(12, 12, 12, 12)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll.setWidget(self._grid_widget)
        ga_layout.addWidget(scroll, 1)

        # Add photos button
        btn_add = QPushButton("+ Add photos")
        btn_add.setProperty("class", "primary")
        btn_add.clicked.connect(self._add_photos)
        ga_layout.addWidget(btn_add, 0, Qt.AlignmentFlag.AlignLeft)

        # Action panel
        self._action_panel = QFrame()
        self._action_panel.setStyleSheet(
            f"QFrame{{background:{COLORS['paper_2']};border-radius:6px;"
            f"border:1px solid {COLORS['paper_3']};}}"
        )
        ap_layout = QHBoxLayout(self._action_panel)
        ap_layout.setContentsMargins(12, 8, 12, 8)
        ap_layout.setSpacing(8)

        self._btn_view = QPushButton("View full size")
        self._btn_view.clicked.connect(self._view_full_size)
        ap_layout.addWidget(self._btn_view)

        self._btn_set_cover = QPushButton("Set as cover")
        self._btn_set_cover.clicked.connect(self._set_as_cover)
        ap_layout.addWidget(self._btn_set_cover)
        ap_layout.addStretch()

        self._action_panel.setVisible(False)
        ga_layout.addWidget(self._action_panel)

        root.addWidget(self._gallery_area, 1)

        self._update_visibility()

    def _update_visibility(self):
        has_id = self.watch_id is not None
        self._unsaved_msg.setVisible(not has_id)
        self._gallery_area.setVisible(has_id)

    def refresh(self, watch_id: int):
        self.watch_id = watch_id
        self._update_visibility()
        self._load_images()

    def _load_images(self):
        self._cards.clear()
        self._selected_id = None
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        images = self.db.get_images(self.watch_id)
        for i, img in enumerate(images):
            full_path = os.path.join(IMAGES_DIR, img["path"])
            card = ThumbnailCard(img["id"], full_path, bool(img["is_cover"]))
            card.clicked.connect(self._on_card_clicked)
            card.delete_req.connect(self._on_delete_req)
            self._grid.addWidget(card, i // COLS, i % COLS)
            self._cards[img["id"]] = card

        self._action_panel.setVisible(False)

    def _on_card_clicked(self, image_id: int):
        if self._selected_id is not None and self._selected_id in self._cards:
            self._cards[self._selected_id].set_selected(False)

        if self._selected_id == image_id:
            self._selected_id = None
            self._action_panel.setVisible(False)
        else:
            self._selected_id = image_id
            self._cards[image_id].set_selected(True)
            self._action_panel.setVisible(True)

    def _on_delete_req(self, image_id: int):
        reply = QMessageBox.question(
            self, "Delete photo", "Remove this photo from the watch?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_image(image_id)
            if self._selected_id == image_id:
                self._selected_id = None
            self._load_images()

    def _add_photos(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select photos", "",
            "Images (*.jpg *.jpeg *.png *.webp)"
        )
        for path in paths:
            self.db.add_image(self.watch_id, path)
        if paths:
            self._load_images()

    def _view_full_size(self):
        if self._selected_id is None:
            return
        images = self.db.get_images(self.watch_id)
        img = next((i for i in images if i["id"] == self._selected_id), None)
        if img:
            dlg = ImageViewerDialog(os.path.join(IMAGES_DIR, img["path"]), self)
            dlg.exec()

    def _set_as_cover(self):
        if self._selected_id is None:
            return
        self.db.set_cover(self.watch_id, self._selected_id)
        self._load_images()
