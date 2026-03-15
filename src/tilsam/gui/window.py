from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QProgressBar,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)

from qt_material import apply_stylesheet

from tilsam.alphabets import get_alphabet
from tilsam.analysis import frequency, tables
from tilsam.ciphers import affine as cipher_affine
from tilsam.ciphers import caesar as cipher_caesar
from tilsam.ciphers import substitution as cipher_substitution
from tilsam.crack import affine as crack_affine
from tilsam.crack import caesar as crack_caesar
from tilsam.crack import substitution as crack_substitution


class CipherChoice(str, Enum):
    CAESAR = "Caesar"
    AFFINE = "Affine"
    SUBSTITUTION = "Substitution"


class LangChoice(str, Enum):
    EN = "English"
    AR = "Arabic"
    FR = "French"


class Operation(str, Enum):
    ENCRYPT = "Encrypt"
    DECRYPT = "Decrypt"
    CRACK = "Crack"


@dataclass(frozen=True)
class Lang:
    value: str


def detect_lang(text: str) -> Lang:
    arabic_count = sum(1 for c in text if 0x0600 <= ord(c) <= 0x06FF)
    latin_count = sum(1 for c in text if c.isascii() and c.isalpha())
    if arabic_count > latin_count:
        return Lang("ar")
    french_accents = set("àâäçèéêëîïôöùûüÿœæÀÂÄÇÈÉÊËÎÏÔÖÙÛÜŸŒÆ")
    if any(c in french_accents for c in text):
        return Lang("fr")
    return Lang("en")


def resolve_lang(lang: str | None, text: str) -> Lang:
    return Lang(lang) if lang is not None else detect_lang(text)


def get_freq_tables(lang: Lang):
    if lang.value == "en":
        return tables.english_letter_freq(), tables.english_bigram_freq()
    if lang.value == "ar":
        return tables.arabic_letter_freq(), tables.arabic_bigram_freq()
    if lang.value == "fr":
        return tables.french_letter_freq(), tables.french_bigram_freq()
    raise ValueError(f"unsupported language: {lang.value!r}")


def format_candidates(candidates, top: int) -> str:
    out_lines: list[str] = []
    for i, c in enumerate(candidates[:top], start=1):
        out_lines.append(f"#{i} [score: {c.score:.4f}] ({c.key_description})")
        out_lines.append(f"  {c.plaintext}")
        out_lines.append("")
    return "\n".join(out_lines).rstrip() + "\n"


class NumericItem(QTableWidgetItem):
    """QTableWidgetItem that sorts numerically instead of lexicographically."""

    def __lt__(self, other: QTableWidgetItem) -> bool:
        try:
            return float(self.text()) < float(other.text())
        except ValueError:
            return super().__lt__(other)


BASE_QSS = """
QMainWindow {
    background-color: #1e1e1e;
}
QWidget#central {
    background-color: #1e1e1e;
}

QWidget#sidebar {
    background-color: #242424;
}

QSplitter::handle {
    background: #2a2a2a;
}
QSplitter::handle:horizontal {
    width: 5px;
}
QSplitter::handle:vertical {
    height: 5px;
}
QSplitter::handle:hover {
    background: #c62828;
}

QLabel#section_label {
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 2px;
    color: #555555;
    background: transparent;
    padding: 0;
    margin: 0;
}
QLabel#pane_label {
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 2px;
    color: #888888;
    background: transparent;
}
QLabel#param_field_label {
    font-size: 14px;
    color: #777777;
    background: transparent;
}
QLabel#no_params_label {
    font-size: 13px;
    color: #555555;
    background: transparent;
    font-style: italic;
}
QLabel#title_label {
    font-size: 20px;
    font-weight: bold;
    letter-spacing: 6px;
    color: #e53935;
    background: transparent;
}
QLabel#version_label {
    font-size: 12px;
    color: #3a3a3a;
    background: transparent;
}

QPushButton#op_btn {
    background: #2c2c2c;
    border: 1px solid #383838;
    border-radius: 5px;
    color: #777777;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 1px;
    min-height: 34px;
    max-height: 34px;
    text-align: left;
    padding-left: 14px;
}
QPushButton#op_btn:checked {
    background: #c62828;
    border-color: #c62828;
    color: #ffffff;
}
QPushButton#op_btn:hover:!checked {
    background: #323232;
    color: #aaaaaa;
    border-color: #444444;
}

QListWidget#cipher_list {
    background: #2c2c2c;
    border: 1px solid #383838;
    border-radius: 6px;
    outline: none;
    font-size: 14px;
    color: #888888;
}
QListWidget#cipher_list::item {
    padding: 9px 14px;
    border-radius: 4px;
    color: #888888;
    border: none;
}
QListWidget#cipher_list::item:selected {
    background: #c62828;
    color: #ffffff;
}
QListWidget#cipher_list::item:hover:!selected {
    background: #333333;
    color: #cccccc;
}

QSpinBox#param_spin,
QLineEdit#param_line {
    background: #2c2c2c;
    border: 1px solid #383838;
    border-radius: 5px;
    color: #cccccc;
    font-size: 14px;
    padding: 5px 8px;
    min-height: 30px;
    selection-background-color: #c62828;
}
QSpinBox#param_spin:focus,
QLineEdit#param_line:focus {
    border-color: #c62828;
    background: #2e2e2e;
}
QSpinBox#param_spin::up-button,
QSpinBox#param_spin::down-button {
    width: 16px;
    background: #383838;
    border: none;
}
QSpinBox#param_spin::up-button:hover,
QSpinBox#param_spin::down-button:hover {
    background: #484848;
}

QComboBox#lang_combo {
    background: #2c2c2c;
    border: 1px solid #383838;
    border-radius: 5px;
    color: #cccccc;
    font-size: 14px;
    padding: 5px 10px;
    min-height: 32px;
    selection-background-color: #c62828;
}
QComboBox#lang_combo::drop-down {
    border: none;
    width: 20px;
    background: transparent;
}
QComboBox#lang_combo QAbstractItemView {
    background: #2c2c2c;
    border: 1px solid #444444;
    selection-background-color: #c62828;
    color: #cccccc;
    font-size: 14px;
    outline: none;
}

QPushButton#execute_btn {
    background: #c62828;
    color: #ffffff;
    border: none;
    border-radius: 5px;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 2px;
    min-height: 38px;
    max-height: 38px;
}
QPushButton#execute_btn:hover  { background: #e53935; }
QPushButton#execute_btn:pressed { background: #b71c1c; }

QTextEdit#io_text {
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    color: #cccccc;
    font-family: monospace;
    font-size: 15px;
    padding: 10px;
    selection-background-color: #c62828;
}

QPushButton#action_btn {
    background: transparent;
    border: 1px solid #333333;
    border-radius: 4px;
    color: #555555;
    font-size: 12px;
    padding: 0 10px;
    min-height: 24px;
    max-height: 24px;
}
QPushButton#action_btn:hover {
    background: #272727;
    color: #999999;
    border-color: #444444;
}
QPushButton#action_btn_accent {
    background: transparent;
    border: 1px solid #6a1515;
    border-radius: 4px;
    color: #c62828;
    font-size: 12px;
    padding: 0 10px;
    min-height: 24px;
    max-height: 24px;
}
QPushButton#action_btn_accent:hover {
    background: #1e1010;
}

QFrame#header_sep {
    background: #2a2a2a;
    max-height: 1px;
    min-height: 1px;
    border: none;
    margin: 0;
}

QWidget#freq_header_widget {
    background: #1e1e1e;
    border-top: 1px solid #2a2a2a;
}

QTableWidget#freq_table {
    background: #161616;
    border: none;
    gridline-color: #1e1e1e;
    font-size: 13px;
    color: #aaaaaa;
    outline: none;
    selection-background-color: #1e1010;
}
QTableWidget#freq_table QHeaderView::section {
    background: #1c1c1c;
    color: #555555;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
    border: none;
    border-bottom: 1px solid #2a2a2a;
    padding: 5px 10px;
}
QTableWidget#freq_table QHeaderView::section:hover {
    background: #222222;
    color: #888888;
}
QTableWidget#freq_table::item {
    padding: 3px 10px;
    border: none;
    color: #aaaaaa;
}
QTableWidget#freq_table::item:selected {
    background: #1e1010;
    color: #dddddd;
}

QStatusBar {
    background: #1a1a1a;
    color: #444444;
    font-size: 12px;
    border-top: 1px solid #272727;
}
"""


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("section_label")
    return lbl


def _pane_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("pane_label")
    return lbl


def _action_btn(text: str, accent: bool = False) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("action_btn_accent" if accent else "action_btn")
    return btn


def _param_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("param_field_label")
    return lbl


def _separator(name: str = "header_sep") -> QFrame:
    f = QFrame()
    f.setObjectName(name)
    return f


def _wrap(layout, name: str = "") -> QWidget:
    w = QWidget()
    if name:
        w.setObjectName(name)
    w.setLayout(layout)
    return w


class OperationSelector(QWidget):
    def __init__(self, labels: list[str], parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._buttons: list[QPushButton] = []
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        for i, label in enumerate(labels):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setObjectName("op_btn")
            self._group.addButton(btn, i)
            layout.addWidget(btn)
            self._buttons.append(btn)

        self._buttons[0].setChecked(True)

    def button(self, index: int) -> QPushButton:
        return self._buttons[index]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Tilsam")
        self.resize(1280, 800)

        app = QGuiApplication.instance()
        apply_stylesheet(app, theme="dark_red.xml")
        app.setStyleSheet(app.styleSheet() + BASE_QSS)

        self.cipher = CipherChoice.CAESAR
        self.lang = LangChoice.EN
        self.operation = Operation.ENCRYPT

        # Raw data kept so bars can be rebuilt after sort
        self._freq_data: list[tuple[str, float]] = []

        # guard to avoid rebuild during analyze/clear
        self._freq_rebuilding = False

        self._build_param_widgets()
        self._build_ui()
        self._refresh_params_ui()

    def _build_param_widgets(self) -> None:
        self.shift_spin = QSpinBox()
        self.shift_spin.setObjectName("param_spin")
        self.shift_spin.setRange(-10_000, 10_000)
        self.shift_spin.setValue(3)

        self.affine_a = QLineEdit("5")
        self.affine_a.setObjectName("param_line")
        self.affine_b = QLineEdit("8")
        self.affine_b.setObjectName("param_line")

        self.sub_key = QLineEdit("")
        self.sub_key.setObjectName("param_line")
        self.sub_key.setPlaceholderText("Permutation of alphabet…")

        self.sub_iterations = QSpinBox()
        self.sub_iterations.setObjectName("param_spin")
        self.sub_iterations.setRange(1, 5_000_000)
        self.sub_iterations.setValue(100)

        self.params_stack = QStackedWidget()
        self.params_stack.setFixedHeight(56)

        self.page_none = QWidget()
        nl = QVBoxLayout(self.page_none)
        nl.setContentsMargins(0, 8, 0, 0)
        lbl = QLabel("No parameters needed.")
        lbl.setObjectName("no_params_label")
        nl.addWidget(lbl)

        self.page_caesar = QWidget()
        fl = QFormLayout(self.page_caesar)
        fl.setContentsMargins(0, 4, 0, 0)
        fl.setHorizontalSpacing(12)
        fl.setVerticalSpacing(4)
        fl.addRow(_param_label("Shift"), self.shift_spin)

        self.page_affine = QWidget()
        row = QHBoxLayout(self.page_affine)
        row.setContentsMargins(0, 8, 0, 0)
        row.setSpacing(8)
        row.addWidget(_param_label("a"))
        row.addWidget(self.affine_a)
        row.addSpacing(8)
        row.addWidget(_param_label("b"))
        row.addWidget(self.affine_b)
        row.addStretch()

        self.page_substitution = QWidget()
        fl2 = QFormLayout(self.page_substitution)
        fl2.setContentsMargins(0, 4, 0, 0)
        fl2.setHorizontalSpacing(12)
        fl2.setVerticalSpacing(4)
        fl2.addRow(_param_label("Key"), self.sub_key)

        self.page_sub_crack = QWidget()
        fl3 = QFormLayout(self.page_sub_crack)
        fl3.setContentsMargins(0, 4, 0, 0)
        fl3.setHorizontalSpacing(12)
        fl3.setVerticalSpacing(4)
        fl3.addRow(_param_label("Iterations"), self.sub_iterations)

        for page in (
            self.page_none,
            self.page_caesar,
            self.page_affine,
            self.page_substitution,
            self.page_sub_crack,
        ):
            self.params_stack.addWidget(page)

    def _build_ui(self) -> None:
        title = QLabel("TILSAM")
        title.setObjectName("title_label")
        version = QLabel("v0.1.0")
        version.setObjectName("version_label")

        hdr = QHBoxLayout()
        hdr.setContentsMargins(0, 0, 0, 8)
        hdr.setSpacing(10)
        hdr.addWidget(title)
        hdr.addWidget(version)
        hdr.addStretch()

        # Sidebar
        self.op_selector = OperationSelector(["Encrypt", "Decrypt", "Crack"])
        self.op_selector.button(0).clicked.connect(lambda: self._set_operation(Operation.ENCRYPT))
        self.op_selector.button(1).clicked.connect(lambda: self._set_operation(Operation.DECRYPT))
        self.op_selector.button(2).clicked.connect(lambda: self._set_operation(Operation.CRACK))

        self.cipher_list = QListWidget()
        self.cipher_list.setObjectName("cipher_list")
        self.cipher_list.setSpacing(1)
        self.cipher_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cipher_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        for cipher in CipherChoice:
            self.cipher_list.addItem(QListWidgetItem(cipher.value))
        self.cipher_list.setCurrentRow(0)
        self.cipher_list.currentTextChanged.connect(self._on_cipher_changed)
        self.cipher_list.setFixedHeight(
            self.cipher_list.sizeHintForRow(0) * self.cipher_list.count()
            + 2 * self.cipher_list.frameWidth()
            + 12
        )

        self.lang_combo = QComboBox()
        self.lang_combo.setObjectName("lang_combo")
        self.lang_combo.addItems([l.value for l in LangChoice])
        self.lang_combo.currentTextChanged.connect(self._on_lang_changed)

        # Encoding (for GUI import/export like CLI)
        self.encoding_combo = QComboBox()
        self.encoding_combo.setObjectName("lang_combo")  # reuse styling
        self.encoding_combo.addItems(["utf-8", "utf-16", "iso-8859-1"])
        self.encoding_combo.setCurrentText("utf-8")

        self.execute_btn = QPushButton("Execute")
        self.execute_btn.setObjectName("execute_btn")
        self.execute_btn.clicked.connect(self._execute)

        sb = QVBoxLayout()
        sb.setContentsMargins(18, 16, 18, 16)
        sb.setSpacing(6)
        sb.addWidget(_section_label("OPERATION"))
        sb.addSpacing(4)
        sb.addWidget(self.op_selector)
        sb.addSpacing(12)
        sb.addWidget(_section_label("CIPHER"))
        sb.addSpacing(4)
        sb.addWidget(self.cipher_list)
        sb.addSpacing(12)
        sb.addWidget(_section_label("PARAMETERS"))
        sb.addSpacing(4)
        sb.addWidget(self.params_stack)
        sb.addSpacing(12)
        sb.addWidget(_section_label("LANGUAGE"))
        sb.addSpacing(4)
        sb.addWidget(self.lang_combo)
        sb.addSpacing(12)
        sb.addWidget(_section_label("ENCODING"))
        sb.addSpacing(4)
        sb.addWidget(self.encoding_combo)
        sb.addStretch()
        sb.addWidget(self.execute_btn)

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setLayout(sb)
        sidebar.setMinimumWidth(180)

        # Input pane
        self.input_text = QTextEdit()
        self.input_text.setObjectName("io_text")
        self.input_text.setPlaceholderText("Enter text here…")

        self.open_in_btn = _action_btn("Open…")
        self.open_in_btn.clicked.connect(lambda: self._open_text_file_into(self.input_text))

        self.save_in_btn = _action_btn("Save…", accent=True)
        self.save_in_btn.clicked.connect(lambda: self._save_text_from(self.input_text))

        self.clear_in_btn = _action_btn("Clear", accent=True)
        self.clear_in_btn.clicked.connect(lambda: self.input_text.setPlainText(""))

        self.swap_btn = _action_btn("Swap ↕")
        self.swap_btn.clicked.connect(self._swap_texts)

        in_hdr = QHBoxLayout()
        in_hdr.setContentsMargins(0, 0, 0, 6)
        in_hdr.setSpacing(6)
        in_hdr.addWidget(_pane_label("INPUT"))
        in_hdr.addStretch()
        in_hdr.addWidget(self.open_in_btn)
        in_hdr.addWidget(self.save_in_btn)
        in_hdr.addWidget(self.clear_in_btn)
        in_hdr.addWidget(self.swap_btn)

        in_layout = QVBoxLayout()
        in_layout.setContentsMargins(0, 0, 0, 0)
        in_layout.setSpacing(0)
        in_layout.addLayout(in_hdr)
        in_layout.addWidget(self.input_text)
        in_w = _wrap(in_layout)

        # Output pane
        self.output_text = QTextEdit()
        self.output_text.setObjectName("io_text")
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Result will appear here…")

        self.save_out_btn = _action_btn("Save…")
        self.save_out_btn.clicked.connect(lambda: self._save_text_from(self.output_text))

        self.clear_out_btn = _action_btn("Clear", accent=True)
        self.clear_out_btn.clicked.connect(lambda: self.output_text.setPlainText(""))

        self.copy_btn = _action_btn("Copy", accent=True)
        self.copy_btn.clicked.connect(self._copy_output)

        out_hdr = QHBoxLayout()
        out_hdr.setContentsMargins(0, 0, 0, 6)
        out_hdr.setSpacing(6)
        out_hdr.addWidget(_pane_label("OUTPUT"))
        out_hdr.addStretch()
        out_hdr.addWidget(self.save_out_btn)
        out_hdr.addWidget(self.clear_out_btn)
        out_hdr.addWidget(self.copy_btn)

        out_layout = QVBoxLayout()
        out_layout.setContentsMargins(0, 0, 0, 0)
        out_layout.setSpacing(0)
        out_layout.addLayout(out_hdr)
        out_layout.addWidget(self.output_text)
        out_w = _wrap(out_layout)

        io_splitter = QSplitter(Qt.Horizontal)
        io_splitter.setHandleWidth(6)
        io_splitter.addWidget(in_w)
        io_splitter.addWidget(out_w)
        io_splitter.setSizes([500, 500])

        # Frequency analysis
        self.analyze_btn = _action_btn("Analyze", accent=True)
        self.analyze_btn.clicked.connect(self._analyze)

        self.clear_freq_btn = _action_btn("Clear", accent=True)
        self.clear_freq_btn.clicked.connect(self._clear_freq)

        freq_hdr = QHBoxLayout()
        freq_hdr.setContentsMargins(10, 8, 10, 6)
        freq_hdr.setSpacing(6)
        freq_hdr.addWidget(_section_label("FREQUENCY ANALYSIS"))
        freq_hdr.addStretch()
        freq_hdr.addWidget(self.clear_freq_btn)
        freq_hdr.addWidget(self.analyze_btn)

        self.freq_table = QTableWidget(0, 3)
        self.freq_table.setObjectName("freq_table")
        self.freq_table.setHorizontalHeaderLabels(["Char", "Freq %", "Distribution"])
        self.freq_table.verticalHeader().setVisible(False)
        self.freq_table.setSortingEnabled(True)
        self.freq_table.setColumnWidth(0, 56)
        self.freq_table.setColumnWidth(1, 76)
        self.freq_table.horizontalHeader().setStretchLastSection(True)
        self.freq_table.setShowGrid(False)
        self.freq_table.horizontalHeader().sortIndicatorChanged.connect(self._rebuild_freq_bars)

        freq_inner = QVBoxLayout()
        freq_inner.setContentsMargins(0, 0, 0, 0)
        freq_inner.setSpacing(0)
        freq_inner.addLayout(freq_hdr)
        freq_inner.addWidget(self.freq_table)

        freq_widget = _wrap(freq_inner, "freq_header_widget")
        freq_widget.setMinimumHeight(80)

        right_vsplit = QSplitter(Qt.Vertical)
        right_vsplit.setHandleWidth(6)
        right_vsplit.addWidget(io_splitter)
        right_vsplit.addWidget(freq_widget)
        right_vsplit.setSizes([520, 220])
        right_vsplit.setCollapsible(0, False)
        right_vsplit.setCollapsible(1, False)

        right_outer = QVBoxLayout()
        right_outer.setContentsMargins(10, 0, 0, 0)
        right_outer.setSpacing(0)
        right_outer.addWidget(right_vsplit)
        right_w = _wrap(right_outer)

        h_splitter = QSplitter(Qt.Horizontal)
        h_splitter.setHandleWidth(6)
        h_splitter.addWidget(sidebar)
        h_splitter.addWidget(right_w)
        h_splitter.setSizes([230, 1050])
        h_splitter.setCollapsible(0, False)
        h_splitter.setCollapsible(1, False)

        root = QVBoxLayout()
        root.setContentsMargins(14, 10, 14, 6)
        root.setSpacing(6)
        root.addLayout(hdr)
        root.addWidget(_separator("header_sep"))
        root.addSpacing(4)
        root.addWidget(h_splitter, stretch=1)

        central = QWidget()
        central.setObjectName("central")
        central.setLayout(root)
        self.setCentralWidget(central)
        self.statusBar().showMessage("Ready")

    # ── GUI file I/O helpers ─────────────────────────────────────────────────

    def _encoding(self) -> str:
        return self.encoding_combo.currentText() if hasattr(self, "encoding_combo") else "utf-8"

    def _open_text_file_into(self, target: QTextEdit) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open text file", "", "Text files (*.txt);;All files (*)"
        )
        if not path:
            return
        try:
            text = Path(path).read_text(encoding=self._encoding())
            target.setPlainText(text)
            self.statusBar().showMessage(f"Loaded: {path}", 2500)
        except Exception as e:
            self.statusBar().showMessage(f"Open failed: {e}", 7000)

    def _save_text_from(self, source: QTextEdit) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save text file", "", "Text files (*.txt);;All files (*)"
        )
        if not path:
            return
        try:
            Path(path).write_text(source.toPlainText(), encoding=self._encoding())
            self.statusBar().showMessage(f"Saved: {path}", 2500)
        except Exception as e:
            self.statusBar().showMessage(f"Save failed: {e}", 7000)

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _make_bar_cell(self, ratio: float) -> QWidget:
        bar = QProgressBar()
        bar.setRange(0, 1000)
        bar.setValue(int(ratio * 1000))
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        bar.setStyleSheet(
            """
            QProgressBar {
                background: #222222;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: #c62828;
                border-radius: 3px;
            }
            """
        )
        cell = QWidget()
        cell.setStyleSheet("background: transparent;")
        cl = QHBoxLayout(cell)
        cl.setContentsMargins(8, 0, 12, 0)
        cl.addWidget(bar)
        return cell

    def _rebuild_freq_bars(self) -> None:
        """Reattach bar widgets after a sort — cell widgets don't move with rows."""
        if self._freq_rebuilding:
            return
        if not self._freq_data:
            return

        max_freq = max(f for _, f in self._freq_data)
        if max_freq == 0:
            return

        self._freq_rebuilding = True
        try:
            freq_map = {ch: f for ch, f in self._freq_data}
            self.freq_table.blockSignals(True)
            for r in range(self.freq_table.rowCount()):
                item = self.freq_table.item(r, 0)
                if not item:
                    continue
                ch = item.text()
                f = freq_map.get(ch, 0.0)
                self.freq_table.setCellWidget(r, 2, self._make_bar_cell(f / max_freq))
        finally:
            self.freq_table.blockSignals(False)
            self._freq_rebuilding = False

    # ── Slots ───────────────────────────────────────────────────────────────

    def _on_cipher_changed(self, text: str) -> None:
        self.cipher = CipherChoice(text)
        self._refresh_params_ui()

    def _on_lang_changed(self, text: str) -> None:
        self.lang = LangChoice(text)

    def _set_operation(self, op: Operation) -> None:
        self.operation = op
        self._refresh_params_ui()

    def _refresh_params_ui(self) -> None:
        if self.operation == Operation.CRACK:
            if self.cipher == CipherChoice.SUBSTITUTION:
                self.params_stack.setCurrentWidget(self.page_sub_crack)
            else:
                self.params_stack.setCurrentWidget(self.page_none)
            return
        if self.cipher == CipherChoice.CAESAR:
            self.params_stack.setCurrentWidget(self.page_caesar)
        elif self.cipher == CipherChoice.AFFINE:
            self.params_stack.setCurrentWidget(self.page_affine)
        elif self.cipher == CipherChoice.SUBSTITUTION:
            self.params_stack.setCurrentWidget(self.page_substitution)
        else:
            self.params_stack.setCurrentWidget(self.page_none)

    def _swap_texts(self) -> None:
        # FIX: true swap (Input <-> Output)
        a = self.input_text.toPlainText()
        b = self.output_text.toPlainText()
        self.input_text.setPlainText(b)
        self.output_text.setPlainText(a)
        self.statusBar().showMessage("Swapped input/output", 1500)

    def _copy_output(self) -> None:
        QGuiApplication.clipboard().setText(self.output_text.toPlainText())
        self.statusBar().showMessage("Copied to clipboard", 2000)

    def _clear_freq(self) -> None:
        # FIX: make clearing deterministic, including bar cell widgets
        self._freq_rebuilding = True
        try:
            self.freq_table.setSortingEnabled(False)
            for r in range(self.freq_table.rowCount()):
                self.freq_table.setCellWidget(r, 2, None)
            self.freq_table.clearContents()
            self.freq_table.setRowCount(0)
            self._freq_data = []
        finally:
            self.freq_table.setSortingEnabled(True)
            self._freq_rebuilding = False
        self.statusBar().showMessage("Cleared frequency analysis", 1500)

    def _lang_code(self) -> str:
        return {"English": "en", "Arabic": "ar", "French": "fr"}[self.lang.value]

    def _execute(self) -> None:
        self.statusBar().showMessage("Working…")
        try:
            text = self.input_text.toPlainText()
            lang = resolve_lang(self._lang_code(), text)
            alpha = get_alphabet(lang.value)
            if self.operation == Operation.ENCRYPT:
                out = self._encrypt(text, alpha)
            elif self.operation == Operation.DECRYPT:
                out = self._decrypt(text, alpha)
            else:
                out = self._crack(text, alpha, lang)
            self.output_text.setPlainText(out)
            self.statusBar().showMessage("Done", 1500)
        except Exception as e:
            self.statusBar().showMessage(f"Error: {e}", 7000)

    def _encrypt(self, text: str, alpha):
        if self.cipher == CipherChoice.CAESAR:
            return cipher_caesar.encrypt(text, int(self.shift_spin.value()), alpha)
        if self.cipher == CipherChoice.AFFINE:
            return cipher_affine.encrypt(
                text, int(self.affine_a.text()), int(self.affine_b.text()), alpha
            )
        if self.cipher == CipherChoice.SUBSTITUTION:
            return cipher_substitution.encrypt(text, self.sub_key.text(), alpha)
        raise ValueError("unsupported cipher")

    def _decrypt(self, text: str, alpha):
        if self.cipher == CipherChoice.CAESAR:
            return cipher_caesar.decrypt(text, int(self.shift_spin.value()), alpha)
        if self.cipher == CipherChoice.AFFINE:
            return cipher_affine.decrypt(
                text, int(self.affine_a.text()), int(self.affine_b.text()), alpha
            )
        if self.cipher == CipherChoice.SUBSTITUTION:
            return cipher_substitution.decrypt(text, self.sub_key.text(), alpha)
        raise ValueError("unsupported cipher")

    def _crack(self, text: str, alpha, lang: Lang):
        letter_freq, bigram_freq = get_freq_tables(lang)
        if self.cipher == CipherChoice.CAESAR:
            candidates = crack_caesar.crack(text, alpha, letter_freq)
            return format_candidates(candidates, 5)
        if self.cipher == CipherChoice.AFFINE:
            candidates = crack_affine.crack(text, alpha, letter_freq)
            return format_candidates(candidates, 5)
        if self.cipher == CipherChoice.SUBSTITUTION:
            candidates = crack_substitution.crack(
                text,
                alpha,
                letter_freq,
                bigram_freq,
                iterations=int(self.sub_iterations.value()),
            )
            return format_candidates(candidates, 5)
        raise ValueError("unsupported cipher")

    def _analyze(self) -> None:
        text = self.input_text.toPlainText()
        if not text.strip():
            self.statusBar().showMessage("Nothing to analyze", 2000)
            return

        lang = resolve_lang(self._lang_code(), text)
        alpha = get_alphabet(lang.value)
        data = frequency.sorted(text, alpha)
        if not data:
            self.statusBar().showMessage("No frequency data", 2000)
            return

        self._freq_data = list(data)
        max_freq = max(f for _, f in self._freq_data) or 1.0

        self._freq_rebuilding = True
        try:
            self.freq_table.setSortingEnabled(False)
            self.freq_table.blockSignals(True)

            self.freq_table.setRowCount(len(self._freq_data))

            for r, (ch, f) in enumerate(self._freq_data):
                self.freq_table.setRowHeight(r, 22)

                char_item = QTableWidgetItem(str(ch))
                char_item.setTextAlignment(Qt.AlignCenter)
                char_item.setForeground(QColor("#cccccc"))
                self.freq_table.setItem(r, 0, char_item)

                pct_item = NumericItem(f"{f * 100:.2f}")
                pct_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                pct_item.setForeground(QColor("#666666"))
                self.freq_table.setItem(r, 1, pct_item)

                self.freq_table.setCellWidget(r, 2, self._make_bar_cell(f / max_freq))
        finally:
            self.freq_table.blockSignals(False)
            self.freq_table.setSortingEnabled(True)
            self._freq_rebuilding = False

        self.statusBar().showMessage("Analysis complete", 2000)
