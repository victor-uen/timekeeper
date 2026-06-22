# ui/watch_form.py
# Formulário de adicionar/editar relógio.
# QDialog é uma janela secundária que aparece sobre a janela principal.
# Os campos são agrupados em abas (QTabWidget) para não sobrecarregar a tela.

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QCheckBox, QTextEdit, QDoubleSpinBox,
    QSpinBox, QTabWidget, QWidget, QPushButton, QLabel,
    QGroupBox, QGridLayout, QDateEdit, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from models import Watch, Category, MOVEMENT_TYPES, MOVEMENT_ORIGINS, CRYSTAL_TYPES, CONDITIONS, STATUSES, CURRENCIES
from typing import List, Optional


class WatchForm(QDialog):
    """
    Janela de formulário para criar ou editar um relógio.
    Recebe um objeto Watch opcional — se None, é um novo relógio.
    """

    def __init__(self, parent, categories: List[Category], watch: Optional[Watch] = None):
        super().__init__(parent)
        self.categories = categories
        self.is_edit = watch is not None
        self.watch = watch or Watch()
        self.rating = self.watch.personal_rating or 0
        self._star_buttons = []

        self.setWindowTitle("Edit watch" if self.is_edit else "Add watch")
        self.setMinimumSize(700, 580)
        self.setModal(True)

        self._build_ui()
        if self.is_edit:
            self._populate_fields()

    # ── Construção da interface ────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Cabeçalho
        header = QFrame()
        header.setStyleSheet("background: white; border-bottom: 1px solid #E5E0D8;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 14, 20, 14)
        title = QLabel("Edit watch" if self.is_edit else "Add watch")
        title.setFont(QFont("Segoe UI", 15))
        header_layout.addWidget(title)
        layout.addWidget(header)

        # Abas — organiza os campos em grupos lógicos
        self.tabs = QTabWidget()
        self.tabs.setContentsMargins(0, 0, 0, 0)

        self.tabs.addTab(self._tab_identity(),    "Identity")
        self.tabs.addTab(self._tab_movement(),    "Movement")
        self.tabs.addTab(self._tab_case_dial(),   "Case & Dial")
        self.tabs.addTab(self._tab_acquisition(), "Acquisition")
        self.tabs.addTab(self._tab_personal(),    "Personal")

        layout.addWidget(self.tabs, 1)

        # Rodapé com botões
        footer = QFrame()
        footer.setStyleSheet("background: white; border-top: 1px solid #E5E0D8;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 12, 20, 12)

        if self.is_edit:
            btn_delete = QPushButton("Delete watch")
            btn_delete.setProperty("class", "danger")
            btn_delete.clicked.connect(self._confirm_delete)
            footer_layout.addWidget(btn_delete)

        footer_layout.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        footer_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Save watch")
        btn_save.setProperty("class", "primary")
        btn_save.clicked.connect(self._save)
        footer_layout.addWidget(btn_save)

        layout.addWidget(footer)

    def _make_form_widget(self) -> tuple:
        """Cria um widget com QFormLayout já configurado. Retorna (widget, layout)."""
        w = QWidget()
        f = QFormLayout(w)
        f.setContentsMargins(20, 20, 20, 20)
        f.setSpacing(10)
        f.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        return w, f

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setProperty("class", "section-title")
        lbl.setStyleSheet("font-size:10px; font-weight:600; letter-spacing:1px; color:#B8945A; text-transform:uppercase; margin-top:8px;")
        return lbl

    # ── Aba: Identidade ────────────────────────────────────────────────────────

    def _tab_identity(self) -> QWidget:
        w, f = self._make_form_widget()

        self.e_brand    = QLineEdit(); self.e_brand.setPlaceholderText("Longines, Grand Seiko…")
        self.e_model    = QLineEdit(); self.e_model.setPlaceholderText("Conquest Heritage, SBGW231…")
        self.e_ref      = QLineEdit(); self.e_ref.setPlaceholderText("L1.611.4.72.4")
        self.e_serial   = QLineEdit(); self.e_serial.setPlaceholderText("12345678")
        self.e_year     = QLineEdit(); self.e_year.setPlaceholderText("1968 or c.1960s")
        self.e_origin   = QLineEdit(); self.e_origin.setPlaceholderText("Japan domestic, Swiss export…")

        self.c_status = QComboBox()
        for s in STATUSES:
            self.c_status.addItem(s.capitalize(), s)

        self.c_category = QComboBox()
        self.c_category.addItem("— Uncategorized —", None)
        for cat in self.categories:
            self.c_category.addItem(cat.name, cat.id)

        f.addRow(self._section_label("Required"), QLabel(""))
        f.addRow("Brand *",  self.e_brand)
        f.addRow("Model *",  self.e_model)
        f.addRow(self._section_label("Identity"), QLabel(""))
        f.addRow("Reference",    self.e_ref)
        f.addRow("Serial no.",   self.e_serial)
        f.addRow("Year made",    self.e_year)
        f.addRow("Origin / market", self.e_origin)
        f.addRow(self._section_label("Classification"), QLabel(""))
        f.addRow("Category", self.c_category)
        f.addRow("Status",   self.c_status)
        return w

    # ── Aba: Movimento ─────────────────────────────────────────────────────────

    def _tab_movement(self) -> QWidget:
        w, f = self._make_form_widget()

        self.c_mvt_type = QComboBox()
        labels = {"": "—", "automatic": "Automatic", "manual": "Manual winding",
                  "quartz": "Quartz", "solar": "Solar", "spring_drive": "Spring Drive", "other": "Other"}
        for val, label in labels.items():
            self.c_mvt_type.addItem(label, val)

        self.e_caliber    = QLineEdit(); self.e_caliber.setPlaceholderText("ETA 2892-A2, L888.4, NH35…")

        self.c_mvt_origin = QComboBox()
        for val in ["", "in-house", "ebauche", "unknown"]:
            self.c_mvt_origin.addItem(val.capitalize() if val else "—", val)

        f.addRow("Movement type",   self.c_mvt_type)
        f.addRow("Caliber",         self.e_caliber)
        f.addRow("Movement origin", self.c_mvt_origin)
        return w

    # ── Aba: Case & Dial ───────────────────────────────────────────────────────

    def _tab_case_dial(self) -> QWidget:
        w, f = self._make_form_widget()

        self.s_diameter  = QDoubleSpinBox(); self.s_diameter.setRange(0, 99); self.s_diameter.setSuffix(" mm"); self.s_diameter.setSpecialValueText("—")
        self.s_thickness = QDoubleSpinBox(); self.s_thickness.setRange(0, 99); self.s_thickness.setSuffix(" mm"); self.s_thickness.setSpecialValueText("—")
        self.e_case_mat  = QLineEdit(); self.e_case_mat.setPlaceholderText("Stainless steel, gold-filled, titanium…")
        self.e_wr        = QLineEdit(); self.e_wr.setPlaceholderText("50m / 5ATM / 3 bar")

        self.c_crystal = QComboBox()
        crystal_labels = {"": "—", "sapphire": "Sapphire", "mineral": "Mineral",
                          "acrylic": "Acrylic / Plexiglass", "hesalite": "Hesalite", "other": "Other"}
        for val, label in crystal_labels.items():
            self.c_crystal.addItem(label, val)

        self.e_dial_color = QLineEdit(); self.e_dial_color.setPlaceholderText("Silvered, black lacquer, blue sunburst…")
        self.e_dial_mat   = QLineEdit(); self.e_dial_mat.setPlaceholderText("Guilloché, enamel, meteorite…")
        self.e_strap      = QLineEdit(); self.e_strap.setPlaceholderText("Brown leather, Jubilee bracelet, NATO…")
        self.e_clasp      = QLineEdit(); self.e_clasp.setPlaceholderText("Stainless steel deployant, tang buckle…")

        f.addRow(self._section_label("Case"), QLabel(""))
        f.addRow("Diameter",      self.s_diameter)
        f.addRow("Thickness",     self.s_thickness)
        f.addRow("Case material", self.e_case_mat)
        f.addRow("Crystal",       self.c_crystal)
        f.addRow("Water resistance", self.e_wr)
        f.addRow(self._section_label("Dial"), QLabel(""))
        f.addRow("Dial color",    self.e_dial_color)
        f.addRow("Dial material", self.e_dial_mat)
        f.addRow(self._section_label("Strap / Bracelet"), QLabel(""))
        f.addRow("Strap material", self.e_strap)
        f.addRow("Clasp material", self.e_clasp)
        return w

    # ── Aba: Aquisição ─────────────────────────────────────────────────────────

    def _tab_acquisition(self) -> QWidget:
        w, f = self._make_form_widget()

        self.e_from      = QLineEdit(); self.e_from.setPlaceholderText("Relojoaria Central, Mercado Livre, particular…")
        self.d_acquired  = QDateEdit(); self.d_acquired.setSpecialValueText("—"); self.d_acquired.setCalendarPopup(True)
        self.d_acquired.setDate(QDate(2000, 1, 1))

        self.s_price_brl  = QDoubleSpinBox(); self.s_price_brl.setRange(0, 9999999); self.s_price_brl.setPrefix("R$ "); self.s_price_brl.setSpecialValueText("—"); self.s_price_brl.setDecimals(2)
        self.s_price_orig = QDoubleSpinBox(); self.s_price_orig.setRange(0, 9999999); self.s_price_orig.setSpecialValueText("—"); self.s_price_orig.setDecimals(2)

        self.c_currency = QComboBox()
        for cur in CURRENCIES:
            self.c_currency.addItem(cur, cur)

        self.c_condition = QComboBox()
        cond_labels = {"": "—", "mint": "Mint", "excellent": "Excellent",
                       "good": "Good", "fair": "Fair", "poor": "Poor"}
        for val, label in cond_labels.items():
            self.c_condition.addItem(label, val)

        self.d_last_svc  = QDateEdit(); self.d_last_svc.setSpecialValueText("—"); self.d_last_svc.setCalendarPopup(True); self.d_last_svc.setDate(QDate(2000, 1, 1))
        self.d_next_svc  = QDateEdit(); self.d_next_svc.setSpecialValueText("—"); self.d_next_svc.setCalendarPopup(True); self.d_next_svc.setDate(QDate(2000, 1, 1))

        # Checkboxes lado a lado
        checks = QWidget()
        cl = QHBoxLayout(checks); cl.setContentsMargins(0,0,0,0); cl.setSpacing(20)
        self.chk_box     = QCheckBox("Box"); cl.addWidget(self.chk_box)
        self.chk_papers  = QCheckBox("Papers"); cl.addWidget(self.chk_papers)
        self.chk_insured = QCheckBox("Insured"); cl.addWidget(self.chk_insured)
        self.chk_sale    = QCheckBox("For sale"); cl.addWidget(self.chk_sale)
        cl.addStretch()

        # Linha de preço original + moeda
        price_row = QWidget()
        pl = QHBoxLayout(price_row); pl.setContentsMargins(0,0,0,0); pl.setSpacing(8)
        pl.addWidget(self.s_price_orig, 1)
        pl.addWidget(self.c_currency)

        f.addRow(self._section_label("Acquisition"), QLabel(""))
        f.addRow("Source",         self.e_from)
        f.addRow("Date acquired",  self.d_acquired)
        f.addRow("Condition",      self.c_condition)
        f.addRow("Price paid (BRL)", self.s_price_brl)
        f.addRow("Price (original cur.)", price_row)
        f.addRow("Documentation", checks)
        f.addRow(self._section_label("Service"), QLabel(""))
        f.addRow("Last service",   self.d_last_svc)
        f.addRow("Next service (est.)", self.d_next_svc)
        return w

    # ── Aba: Pessoal ───────────────────────────────────────────────────────────

    def _tab_personal(self) -> QWidget:
        w, f = self._make_form_widget()

        # Rating em estrelas
        stars_widget = QWidget()
        sl = QHBoxLayout(stars_widget); sl.setContentsMargins(0,0,0,0); sl.setSpacing(4)
        for i in range(1, 6):
            btn = QPushButton("★")
            btn.setFixedSize(32, 32)
            btn.setStyleSheet("border:none; font-size:20px; color:#E5E0D8; background:transparent;")
            btn.clicked.connect(lambda _, v=i: self._set_rating(v))
            self._star_buttons.append(btn)
            sl.addWidget(btn)
        sl.addStretch()
        self._update_stars()

        self.e_notes = QTextEdit()
        self.e_notes.setPlaceholderText(
            "Condition details, provenance, history, modifications, "
            "interesting facts about this piece…"
        )
        self.e_notes.setMinimumHeight(100)

        f.addRow("Personal rating", stars_widget)
        f.addRow("Notes", self.e_notes)
        return w

    # ── Rating ─────────────────────────────────────────────────────────────────

    def _set_rating(self, value: int):
        # Se clicar na mesma estrela que já está selecionada, limpa o rating
        self.rating = 0 if self.rating == value else value
        self._update_stars()

    def _update_stars(self):
        for i, btn in enumerate(self._star_buttons):
            color = "#B8945A" if i < self.rating else "#E5E0D8"
            btn.setStyleSheet(f"border:none; font-size:20px; color:{color}; background:transparent;")

    # ── Populate / Save ────────────────────────────────────────────────────────

    def _populate_fields(self):
        """Preenche os campos com os dados do relógio sendo editado."""
        w = self.watch

        self.e_brand.setText(w.brand or "")
        self.e_model.setText(w.model or "")
        self.e_ref.setText(w.reference or "")
        self.e_serial.setText(w.serial_number or "")
        self.e_year.setText(w.year_made or "")
        self.e_origin.setText(w.origin_market or "")

        # ComboBox: seleciona pelo valor de dados (userData), não pelo texto
        self._set_combo(self.c_status, w.status)
        self._set_combo(self.c_category, w.category_id)
        self._set_combo(self.c_mvt_type, w.movement_type or "")
        self.e_caliber.setText(w.caliber or "")
        self._set_combo(self.c_mvt_origin, w.movement_origin or "")

        if w.case_diameter: self.s_diameter.setValue(w.case_diameter)
        if w.case_thickness: self.s_thickness.setValue(w.case_thickness)
        self.e_case_mat.setText(w.case_material or "")
        self._set_combo(self.c_crystal, w.crystal or "")
        self.e_wr.setText(w.water_resistance or "")
        self.e_dial_color.setText(w.dial_color or "")
        self.e_dial_mat.setText(w.dial_material or "")
        self.e_strap.setText(w.strap_material or "")
        self.e_clasp.setText(w.clasp_material or "")

        self.e_from.setText(w.acquired_from or "")
        if w.acquired_date:
            self.d_acquired.setDate(QDate.fromString(w.acquired_date, "yyyy-MM-dd"))
        if w.price_brl: self.s_price_brl.setValue(w.price_brl)
        if w.price_original: self.s_price_orig.setValue(w.price_original)
        self._set_combo(self.c_currency, w.price_currency or "BRL")
        self._set_combo(self.c_condition, w.condition or "")
        self.chk_box.setChecked(w.has_box)
        self.chk_papers.setChecked(w.has_papers)
        self.chk_insured.setChecked(w.is_insured)
        self.chk_sale.setChecked(w.is_for_sale)

        if w.last_service:
            self.d_last_svc.setDate(QDate.fromString(w.last_service, "yyyy-MM-dd"))
        if w.next_service:
            self.d_next_svc.setDate(QDate.fromString(w.next_service, "yyyy-MM-dd"))

        self.rating = w.personal_rating or 0
        self._update_stars()
        self.e_notes.setPlainText(w.notes or "")

    def _set_combo(self, combo: QComboBox, value):
        """Seleciona um item do ComboBox pelo valor de dados (userData)."""
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return

    def _save(self):
        """Valida os campos obrigatórios e salva o relógio."""
        brand = self.e_brand.text().strip()
        model = self.e_model.text().strip()

        if not brand or not model:
            QMessageBox.warning(self, "Required fields", "Brand and Model are required.")
            return

        w = self.watch
        w.brand            = brand
        w.model            = model
        w.reference        = self.e_ref.text().strip() or None
        w.serial_number    = self.e_serial.text().strip() or None
        w.year_made        = self.e_year.text().strip() or None
        w.origin_market    = self.e_origin.text().strip() or None
        w.status           = self.c_status.currentData()
        w.category_id      = self.c_category.currentData()
        w.movement_type    = self.c_mvt_type.currentData() or None
        w.caliber          = self.e_caliber.text().strip() or None
        w.movement_origin  = self.c_mvt_origin.currentData() or None
        w.case_diameter    = self.s_diameter.value() or None
        w.case_thickness   = self.s_thickness.value() or None
        w.case_material    = self.e_case_mat.text().strip() or None
        w.crystal          = self.c_crystal.currentData() or None
        w.water_resistance = self.e_wr.text().strip() or None
        w.dial_color       = self.e_dial_color.text().strip() or None
        w.dial_material    = self.e_dial_mat.text().strip() or None
        w.strap_material   = self.e_strap.text().strip() or None
        w.clasp_material   = self.e_clasp.text().strip() or None
        w.acquired_from    = self.e_from.text().strip() or None
        d = self.d_acquired.date()
        w.acquired_date    = d.toString("yyyy-MM-dd") if d.year() > 2000 else None
        w.price_brl        = self.s_price_brl.value() or None
        w.price_original   = self.s_price_orig.value() or None
        w.price_currency   = self.c_currency.currentData() or "BRL"
        w.condition        = self.c_condition.currentData() or None
        w.has_box          = self.chk_box.isChecked()
        w.has_papers       = self.chk_papers.isChecked()
        w.is_insured       = self.chk_insured.isChecked()
        w.is_for_sale      = self.chk_sale.isChecked()
        ls = self.d_last_svc.date()
        w.last_service     = ls.toString("yyyy-MM-dd") if ls.year() > 2000 else None
        ns = self.d_next_svc.date()
        w.next_service     = ns.toString("yyyy-MM-dd") if ns.year() > 2000 else None
        w.personal_rating  = self.rating or None
        w.notes            = self.e_notes.toPlainText().strip() or None

        self.accept()  # Fecha o diálogo com resultado "aceito"

    def _confirm_delete(self):
        reply = QMessageBox.question(
            self, "Delete watch",
            f"Remove {self.watch.brand} {self.watch.model} from your collection?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.watch._delete = True  # Flag para a janela principal deletar
            self.accept()

    def get_watch(self) -> Watch:
        return self.watch
