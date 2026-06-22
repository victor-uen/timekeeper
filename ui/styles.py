# ui/styles.py
# Define o tema visual do TimeKeeper.
# PyQt6 usa QSS (Qt Style Sheets), uma linguagem parecida com CSS.
# Centralizar os estilos aqui facilita mudar o visual sem tocar na lógica.

# Paleta de cores
COLORS = {
    "ink":        "#1A1815",   # Texto principal — quase preto, mais quente que #000
    "ink_2":      "#4A4640",   # Texto secundário
    "ink_3":      "#8A857E",   # Texto terciário / hints
    "paper":      "#F7F4EF",   # Fundo principal — branco quente
    "paper_2":    "#EFEBE4",   # Superfícies secundárias
    "paper_3":    "#E5E0D8",   # Bordas e divisores
    "gold":       "#B8945A",   # Acento dourado — remete a relógios
    "gold_light": "#D4AF7A",
    "white":      "#FFFFFF",
    "danger":     "#8B2020",
    "success":    "#1A4731",
}

# Stylesheet global do app
APP_STYLE = f"""
/* ── Janela e fundo geral ── */
QMainWindow, QDialog {{
    background-color: {COLORS['paper']};
}}

QWidget {{
    font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: {COLORS['ink']};
}}

/* ── Barra de menu ── */
QMenuBar {{
    background-color: {COLORS['paper']};
    border-bottom: 1px solid {COLORS['paper_3']};
    padding: 2px 8px;
}}

QMenuBar::item {{
    padding: 4px 12px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {COLORS['paper_2']};
}}

QMenu {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['paper_3']};
    border-radius: 6px;
    padding: 4px;
}}

QMenu::item {{
    padding: 6px 20px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS['paper_2']};
}}

/* ── Labels ── */
QLabel {{
    color: {COLORS['ink']};
    background: transparent;
}}

QLabel[class="section-title"] {{
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
    color: {COLORS['gold']};
    text-transform: uppercase;
}}

QLabel[class="stat-value"] {{
    font-size: 26px;
    font-weight: 300;
    color: {COLORS['ink']};
}}

QLabel[class="stat-label"] {{
    font-size: 11px;
    color: {COLORS['ink_3']};
    text-transform: uppercase;
    letter-spacing: 1px;
}}

QLabel[class="brand-label"] {{
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    color: {COLORS['gold']};
    text-transform: uppercase;
}}

QLabel[class="model-label"] {{
    font-size: 16px;
    color: {COLORS['ink']};
}}

/* ── Inputs ── */
QLineEdit, QTextEdit, QDateEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['paper_3']};
    border-radius: 4px;
    padding: 6px 10px;
    color: {COLORS['ink']};
    selection-background-color: {COLORS['gold_light']};
}}

QLineEdit:focus, QTextEdit:focus, QDateEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {COLORS['gold']};
    outline: none;
}}

QComboBox {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['paper_3']};
    border-radius: 4px;
    padding: 6px 10px;
    color: {COLORS['ink']};
}}

QComboBox:focus {{
    border-color: {COLORS['gold']};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['paper_3']};
    selection-background-color: {COLORS['paper_2']};
    selection-color: {COLORS['ink']};
    outline: none;
}}

/* ── Botões ── */
QPushButton {{
    background-color: transparent;
    border: 1px solid {COLORS['paper_3']};
    border-radius: 4px;
    padding: 7px 18px;
    color: {COLORS['ink_2']};
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: {COLORS['paper_2']};
    border-color: {COLORS['paper_3']};
}}

QPushButton:pressed {{
    background-color: {COLORS['paper_3']};
}}

QPushButton[class="primary"] {{
    background-color: {COLORS['ink']};
    border-color: {COLORS['ink']};
    color: {COLORS['paper']};
    font-weight: 500;
}}

QPushButton[class="primary"]:hover {{
    background-color: {COLORS['ink_2']};
    border-color: {COLORS['ink_2']};
}}

QPushButton[class="danger"] {{
    border-color: #FECACA;
    color: {COLORS['danger']};
}}

QPushButton[class="danger"]:hover {{
    background-color: #FEF2F2;
}}

/* ── Tabela principal ── */
QTableWidget {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['paper_3']};
    border-radius: 6px;
    gridline-color: {COLORS['paper_2']};
    outline: none;
}}

QTableWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid {COLORS['paper_2']};
    color: {COLORS['ink']};
}}

QTableWidget::item:selected {{
    background-color: {COLORS['paper_2']};
    color: {COLORS['ink']};
}}

QHeaderView::section {{
    background-color: {COLORS['paper']};
    border: none;
    border-bottom: 1px solid {COLORS['paper_3']};
    padding: 8px 12px;
    font-size: 11px;
    font-weight: 600;
    color: {COLORS['ink_3']};
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}

/* ── Scroll bars ── */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['paper_3']};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['ink_3']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
}}

QScrollBar::handle:horizontal {{
    background: {COLORS['paper_3']};
    border-radius: 4px;
}}

/* ── Tabs ── */
QTabWidget::pane {{
    border: 1px solid {COLORS['paper_3']};
    border-radius: 6px;
    background: {COLORS['white']};
}}

QTabBar::tab {{
    background: transparent;
    border: none;
    padding: 8px 20px;
    color: {COLORS['ink_3']};
    font-size: 13px;
}}

QTabBar::tab:selected {{
    color: {COLORS['ink']};
    border-bottom: 2px solid {COLORS['gold']};
    font-weight: 500;
}}

QTabBar::tab:hover {{
    color: {COLORS['ink']};
}}

/* ── Checkbox ── */
QCheckBox {{
    spacing: 8px;
    color: {COLORS['ink_2']};
}}

QCheckBox::indicator {{
    width: 15px;
    height: 15px;
    border: 1px solid {COLORS['paper_3']};
    border-radius: 3px;
    background: {COLORS['white']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['ink']};
    border-color: {COLORS['ink']};
    image: none;
}}

/* ── Splitter ── */
QSplitter::handle {{
    background: {COLORS['paper_3']};
    width: 1px;
}}

/* ── Frames / cards ── */
QFrame[class="card"] {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['paper_3']};
    border-radius: 8px;
}}

QFrame[class="stat-card"] {{
    background-color: {COLORS['paper_2']};
    border: none;
    border-radius: 6px;
}}

/* ── Search bar ── */
QLineEdit[class="search"] {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['paper_3']};
    border-radius: 4px;
    padding: 7px 12px 7px 34px;
    font-size: 13px;
}}

/* ── Status badges (simulados com QLabel) ── */
QLabel[class="badge-owned"]    {{ color: #065F46; background: #ECFDF5; border-radius: 3px; padding: 2px 8px; font-size: 11px; }}
QLabel[class="badge-wishlist"] {{ color: #92400E; background: #FEF3C7; border-radius: 3px; padding: 2px 8px; font-size: 11px; }}
QLabel[class="badge-sold"]     {{ color: #6B7280; background: #F3F4F6; border-radius: 3px; padding: 2px 8px; font-size: 11px; }}
QLabel[class="badge-loaned"]   {{ color: #1E40AF; background: #EFF6FF; border-radius: 3px; padding: 2px 8px; font-size: 11px; }}

/* ── Group Box ── */
QGroupBox {{
    border: 1px solid {COLORS['paper_3']};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 8px;
    font-size: 10px;
    font-weight: 600;
    color: {COLORS['gold']};
    letter-spacing: 1px;
    text-transform: uppercase;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    left: 12px;
}}
"""
