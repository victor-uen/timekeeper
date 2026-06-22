# ui/main_window.py
# Janela principal do TimeKeeper.
# QMainWindow é o tipo de janela raiz do PyQt6 — tem barra de menu,
# barra de status, e uma área central para o conteúdo principal.

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QFrame, QSplitter, QHeaderView, QAbstractItemView,
    QDialog, QFormLayout, QColorDialog, QMessageBox, QGridLayout,
    QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon, QAction
from database import Database
from models import Watch, Category
from ui.watch_form import WatchForm
from ui.styles import COLORS


class MainWindow(QMainWindow):
    """
    Janela principal do app.
    Estrutura: barra de topo → painel lateral (categorias) + área principal (tabela + stats)
    """

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_category_id = None   # None = "All"
        self.current_status = "owned"     # Vista atual

        self.setWindowTitle("TimeKeeper")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)

        self._build_menu()
        self._build_ui()
        self._refresh()

    # ── Menu ──────────────────────────────────────────────────────────────────

    def _build_menu(self):
        menubar = self.menuBar()

        # Menu File
        file_menu = menubar.addMenu("File")
        add_action = QAction("Add watch", self)
        add_action.setShortcut("Ctrl+N")
        add_action.triggered.connect(self._open_add_form)
        file_menu.addAction(add_action)

        file_menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Menu View
        view_menu = menubar.addMenu("View")
        for label, status in [("Collection", "owned"), ("Wishlist", "wishlist"),
                               ("Sold", "sold"), ("Loaned out", "loaned")]:
            action = QAction(label, self)
            action.triggered.connect(lambda _, s=status: self._set_status_view(s))
            view_menu.addAction(action)

    # ── Interface principal ───────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Barra de topo ──────────────────────────────────────────────────
        topbar = QFrame()
        topbar.setStyleSheet(f"background:{COLORS['paper']}; border-bottom:1px solid {COLORS['paper_3']};")
        topbar.setFixedHeight(56)
        tl = QHBoxLayout(topbar)
        tl.setContentsMargins(20, 0, 20, 0)
        tl.setSpacing(12)

        # Logo
        logo = QLabel("TimeKeeper")
        logo.setFont(QFont("Segoe UI", 16, QFont.Weight.Light))
        logo.setStyleSheet(f"color:{COLORS['ink']}; letter-spacing:2px;")
        tl.addWidget(logo)

        tl.addSpacing(16)

        # Abas de status (Collection / Wishlist / Sold / Loaned)
        self._status_btns = {}
        for label, status in [("Collection", "owned"), ("Wishlist", "wishlist"),
                               ("Sold", "sold"), ("Loaned", "loaned")]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setStyleSheet(self._nav_btn_style(False))
            btn.clicked.connect(lambda _, s=status: self._set_status_view(s))
            self._status_btns[status] = btn
            tl.addWidget(btn)

        self._status_btns["owned"].setChecked(True)
        self._update_nav_styles()

        tl.addStretch()

        # Busca
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search brand, model, caliber…")
        self.search_input.setFixedWidth(240)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background:{COLORS['white']}; border:1px solid {COLORS['paper_3']};
                border-radius:4px; padding:6px 12px; font-size:13px;
            }}
            QLineEdit:focus {{ border-color:{COLORS['gold']}; }}
        """)
        # Timer para não buscar a cada tecla, só 300ms após parar de digitar
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._refresh_table)
        self.search_input.textChanged.connect(lambda: self._search_timer.start(300))
        tl.addWidget(self.search_input)

        # Botão de adicionar
        btn_add = QPushButton("+ Add watch")
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background:{COLORS['ink']}; color:{COLORS['paper']};
                border:none; border-radius:4px; padding:7px 16px; font-size:13px; font-weight:500;
            }}
            QPushButton:hover {{ background:{COLORS['ink_2']}; }}
        """)
        btn_add.clicked.connect(self._open_add_form)
        tl.addWidget(btn_add)

        root.addWidget(topbar)

        # ── Corpo principal: sidebar + conteúdo ────────────────────────────
        body = QSplitter(Qt.Orientation.Horizontal)
        body.setHandleWidth(1)
        body.setStyleSheet(f"QSplitter::handle {{ background:{COLORS['paper_3']}; }}")

        # Sidebar (categorias)
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(f"background:{COLORS['paper']}; border-right:1px solid {COLORS['paper_3']};")
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(12, 16, 12, 16)
        sl.setSpacing(4)

        cat_header = QHBoxLayout()
        cat_lbl = QLabel("CATEGORIES")
        cat_lbl.setStyleSheet(f"font-size:10px; font-weight:600; color:{COLORS['ink_3']}; letter-spacing:1px;")
        cat_header.addWidget(cat_lbl)
        cat_header.addStretch()
        btn_manage = QPushButton("⚙")
        btn_manage.setFixedSize(22, 22)
        btn_manage.setStyleSheet("border:none; color:#8A857E; background:transparent; font-size:13px;")
        btn_manage.setToolTip("Manage categories")
        btn_manage.clicked.connect(self._open_category_manager)
        cat_header.addWidget(btn_manage)
        sl.addLayout(cat_header)

        sl.addSpacing(6)
        self.cat_list_layout = QVBoxLayout()
        self.cat_list_layout.setSpacing(2)
        sl.addLayout(self.cat_list_layout)
        sl.addStretch()

        body.addWidget(sidebar)

        # Área principal
        main_area = QWidget()
        main_area.setStyleSheet(f"background:{COLORS['paper']};")
        ml = QVBoxLayout(main_area)
        ml.setContentsMargins(20, 20, 20, 20)
        ml.setSpacing(16)

        # Cards de estatísticas
        self.stats_frame = QFrame()
        self.stats_layout = QHBoxLayout(self.stats_frame)
        self.stats_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_layout.setSpacing(12)
        ml.addWidget(self.stats_frame)

        # Tabela de relógios
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Brand", "Model", "Reference", "Year", "Caliber", "Price (BRL)", "Rating"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setShowGrid(False)
        self.table.doubleClicked.connect(self._on_row_double_click)
        self.table.setStyleSheet(f"""
            QTableWidget {{ background:{COLORS['white']}; border:1px solid {COLORS['paper_3']}; border-radius:6px; outline:none; }}
            QTableWidget::item {{ padding:10px 12px; border-bottom:1px solid {COLORS['paper_2']}; }}
            QTableWidget::item:selected {{ background:{COLORS['paper_2']}; color:{COLORS['ink']}; }}
            QHeaderView::section {{ background:{COLORS['paper']}; border:none; border-bottom:1px solid {COLORS['paper_3']}; padding:8px 12px; font-size:11px; font-weight:600; color:{COLORS['ink_3']}; }}
        """)
        ml.addWidget(self.table, 1)

        body.addWidget(main_area)
        body.setSizes([200, 800])

        root.addWidget(body, 1)

        # Barra de status (rodapé)
        self.statusBar().setStyleSheet(f"color:{COLORS['ink_3']}; font-size:12px;")

    # ── Refresh / render ──────────────────────────────────────────────────────

    def _refresh(self):
        """Recarrega categorias, stats e tabela."""
        self.categories = self.db.get_categories()
        self._render_category_sidebar()
        self._render_stats()
        self._refresh_table()

    def _refresh_table(self):
        search = self.search_input.text().strip() or None
        watches = self.db.get_watches(
            status_filter=self.current_status,
            category_id=self.current_category_id,
            search=search
        )
        self._render_table(watches)

    def _render_category_sidebar(self):
        """Reconstrói os botões de categoria no sidebar."""
        # Limpa botões anteriores
        while self.cat_list_layout.count():
            item = self.cat_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Botão "All"
        btn_all = self._cat_button("All", None, self.current_category_id is None)
        self.cat_list_layout.addWidget(btn_all)

        for cat in self.categories:
            btn = self._cat_button(cat.name, cat.id, self.current_category_id == cat.id, cat.color)
            self.cat_list_layout.addWidget(btn)

    def _cat_button(self, label: str, cat_id, active: bool, color: str = None) -> QPushButton:
        btn = QPushButton(label)
        bg = COLORS['paper_3'] if active else "transparent"
        btn.setStyleSheet(f"""
            QPushButton {{
                text-align:left; padding:6px 10px; border:none; border-radius:4px;
                background:{bg}; color:{COLORS['ink_2']}; font-size:13px;
            }}
            QPushButton:hover {{ background:{COLORS['paper_3']}; }}
        """)
        if color:
            dot = "● "
            btn.setText(f"  {label}")
        btn.clicked.connect(lambda: self._set_category(cat_id))
        return btn

    def _render_stats(self):
        stats = self.db.get_stats()
        # Limpa cards anteriores
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cards = [
            ("In collection", str(stats["owned"]), "pieces owned"),
            ("Wishlist", str(stats["wishlist"]), "pieces of interest"),
            ("Total invested", f"R$ {stats['total_brl']:,.0f}", "owned pieces only"),
            ("Avg. rating", str(stats["avg_rating"]) if stats["avg_rating"] else "—", "personal satisfaction"),
        ]

        for title, value, sub in cards:
            card = QFrame()
            card.setStyleSheet(f"background:{COLORS['paper_2']}; border-radius:6px;")
            card.setFixedHeight(80)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 10, 14, 10)
            cl.setSpacing(2)

            lbl = QLabel(title)
            lbl.setStyleSheet(f"font-size:10px; font-weight:600; color:{COLORS['ink_3']}; letter-spacing:1px; background:transparent;")
            val = QLabel(value)
            val.setStyleSheet(f"font-size:22px; font-weight:300; color:{COLORS['ink']}; background:transparent;")
            sub_lbl = QLabel(sub)
            sub_lbl.setStyleSheet(f"font-size:11px; color:{COLORS['ink_3']}; background:transparent;")

            cl.addWidget(lbl)
            cl.addWidget(val)
            cl.addWidget(sub_lbl)
            self.stats_layout.addWidget(card)

    def _render_table(self, watches: list):
        self.table.setRowCount(0)
        for w in watches:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Guarda o ID do relógio na linha para recuperar ao clicar
            id_item = QTableWidgetItem(w.brand)
            id_item.setData(Qt.ItemDataRole.UserRole, w.id)
            self.table.setItem(row, 0, id_item)

            self.table.setItem(row, 1, QTableWidgetItem(w.model))
            self.table.setItem(row, 2, QTableWidgetItem(w.reference or ""))
            self.table.setItem(row, 3, QTableWidgetItem(w.year_made or ""))
            self.table.setItem(row, 4, QTableWidgetItem(w.caliber or ""))
            price = f"R$ {w.price_brl:,.2f}" if w.price_brl else ""
            self.table.setItem(row, 5, QTableWidgetItem(price))
            stars = ("★" * (w.personal_rating or 0)) + ("☆" * (5 - (w.personal_rating or 0)))
            self.table.setItem(row, 6, QTableWidgetItem(stars))

            self.table.setRowHeight(row, 44)

        self.statusBar().showMessage(f"{len(watches)} watch{'es' if len(watches) != 1 else ''}")

    # ── Navegação ─────────────────────────────────────────────────────────────

    def _set_status_view(self, status: str):
        self.current_status = status
        self.current_category_id = None
        self._update_nav_styles()
        self._refresh()

    def _set_category(self, cat_id):
        self.current_category_id = cat_id
        self._render_category_sidebar()
        self._refresh_table()

    def _update_nav_styles(self):
        for status, btn in self._status_btns.items():
            active = status == self.current_status
            btn.setStyleSheet(self._nav_btn_style(active))
            btn.setChecked(active)

    def _nav_btn_style(self, active: bool) -> str:
        color = COLORS['ink'] if active else COLORS['ink_3']
        weight = "500" if active else "400"
        border = f"border-bottom:2px solid {COLORS['gold']};" if active else "border:none;"
        return f"""
            QPushButton {{
                background:transparent; {border}
                border-radius:0; padding:6px 14px;
                color:{color}; font-size:13px; font-weight:{weight};
            }}
            QPushButton:hover {{ color:{COLORS['ink']}; }}
        """

    # ── Formulário de relógio ─────────────────────────────────────────────────

    def _open_add_form(self):
        form = WatchForm(self, self.categories)
        if form.exec() == QDialog.DialogCode.Accepted:
            watch = form.get_watch()
            self.db.save_watch(watch)
            self._refresh()

    def _on_row_double_click(self, index):
        watch_id = self.table.item(index.row(), 0).data(Qt.ItemDataRole.UserRole)
        watch = self.db.get_watch(watch_id)
        if not watch:
            return
        form = WatchForm(self, self.categories, watch)
        if form.exec() == QDialog.DialogCode.Accepted:
            w = form.get_watch()
            if getattr(w, "_delete", False):
                self.db.delete_watch(w.id)
            else:
                self.db.save_watch(w)
            self._refresh()

    # ── Gerenciador de categorias ─────────────────────────────────────────────

    def _open_category_manager(self):
        dlg = CategoryManagerDialog(self, self.db)
        dlg.exec()
        self._refresh()

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        self.db.close()
        event.accept()


class CategoryManagerDialog(QDialog):
    """Janela para criar e remover categorias."""

    def __init__(self, parent, db: Database):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Manage categories")
        self.setFixedSize(380, 480)
        self.setModal(True)
        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Categories"))

        self.list_frame = QVBoxLayout()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.list_frame)
        scroll = QScrollArea()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:1px solid #E5E0D8; border-radius:6px; background:white;")
        layout.addWidget(scroll, 1)

        # Linha de adicionar nova categoria
        add_row = QHBoxLayout()
        self.color_btn = QPushButton("  ")
        self.color_btn.setFixedSize(36, 32)
        self.color_btn.setStyleSheet("background:#6B7280; border:1px solid #E5E0D8; border-radius:4px;")
        self.color_btn.clicked.connect(self._pick_color)
        self.selected_color = "#6B7280"

        self.new_name = QLineEdit()
        self.new_name.setPlaceholderText("New category name")
        self.new_name.returnPressed.connect(self._add_category)

        btn_add = QPushButton("Add")
        btn_add.setStyleSheet(f"background:{COLORS['ink']}; color:white; border:none; border-radius:4px; padding:7px 14px;")
        btn_add.clicked.connect(self._add_category)

        add_row.addWidget(self.color_btn)
        add_row.addWidget(self.new_name, 1)
        add_row.addWidget(btn_add)
        layout.addLayout(add_row)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _load(self):
        # Limpa lista
        while self.list_frame.count():
            item = self.list_frame.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        categories = self.db.get_categories()
        for cat in categories:
            row = QFrame()
            rl = QHBoxLayout(row)
            rl.setContentsMargins(10, 6, 10, 6)

            dot = QLabel("●")
            dot.setStyleSheet(f"color:{cat.color}; font-size:14px;")
            rl.addWidget(dot)

            name_lbl = QLabel(cat.name)
            name_lbl.setStyleSheet("font-size:13px;")
            rl.addWidget(name_lbl, 1)

            if cat.is_default:
                default_lbl = QLabel("default")
                default_lbl.setStyleSheet(f"font-size:11px; color:{COLORS['ink_3']};")
                rl.addWidget(default_lbl)
            else:
                del_btn = QPushButton("×")
                del_btn.setFixedSize(24, 24)
                del_btn.setStyleSheet(f"border:none; color:{COLORS['ink_3']}; background:transparent; font-size:16px;")
                del_btn.clicked.connect(lambda _, cid=cat.id, cname=cat.name: self._delete_category(cid, cname))
                rl.addWidget(del_btn)

            self.list_frame.addWidget(row)

        self.list_frame.addStretch()

    def _pick_color(self):
        color = QColorDialog.getColor(QColor(self.selected_color), self)
        if color.isValid():
            self.selected_color = color.name()
            self.color_btn.setStyleSheet(
                f"background:{self.selected_color}; border:1px solid #E5E0D8; border-radius:4px;"
            )

    def _add_category(self):
        name = self.new_name.text().strip()
        if not name:
            return
        self.db.add_category(name, self.selected_color)
        self.new_name.clear()
        self._load()

    def _delete_category(self, cat_id: int, cat_name: str):
        reply = QMessageBox.question(
            self, "Delete category",
            f"Delete '{cat_name}'? Watches in this category will become uncategorized.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_category(cat_id)
            self._load()
