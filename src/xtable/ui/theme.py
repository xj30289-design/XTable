from __future__ import annotations


THEMES = {
    "light": {
        "window_bg": "#f6f7f8",
        "panel_bg": "#ffffff",
        "toolbar_bg": "#f9fafb",
        "workspace_bg": "#ffffff",
        "text": "#1f2933",
        "muted": "#697586",
        "border": "#d8dee6",
        "accent": "#0f766e",
        "hover_bg": "#eef2f5",
        "active_bg": "#dff7f2",
        "disabled_text": "#98a2b3",
        "drawer_border": "#cfd7df",
        "shadow_border": "#e5e9ef",
        "dialog_bg": "#ffffff",
        "dialog_button_bg": "#f3f6f8",
        "danger": "#dc2626",
        "form_panel_bg": "#ffffff",
        "table_error_bg": "#fee2e2",
        "table_warning_bg": "#fef3c7",
        "selection_bg": "#0f766e",
        "selection_text": "#ffffff",
        "selection_border": "#0b5f58",
        "selection_inactive_bg": "#d9ebe8",
    },
    "dark": {
        "window_bg": "#15181c",
        "panel_bg": "#20252b",
        "toolbar_bg": "#1b2026",
        "workspace_bg": "#181c21",
        "text": "#e7edf3",
        "muted": "#a4afbd",
        "border": "#38414d",
        "accent": "#2dd4bf",
        "hover_bg": "#2a3139",
        "active_bg": "#123f3a",
        "disabled_text": "#697586",
        "drawer_border": "#303842",
        "shadow_border": "#12161b",
        "dialog_bg": "#20252b",
        "dialog_button_bg": "#28303a",
        "danger": "#f87171",
        "form_panel_bg": "#1b2026",
        "table_error_bg": "#4a1f25",
        "table_warning_bg": "#473a18",
        "selection_bg": "#2dd4bf",
        "selection_text": "#081311",
        "selection_border": "#5eead4",
        "selection_inactive_bg": "#24413e",
    },
}


def build_stylesheet(theme: str) -> str:
    tokens = THEMES[theme]
    return f"""
    /* drawer_border: {tokens["drawer_border"]}; shadow_border: {tokens["shadow_border"]}; dialog_bg: {tokens["dialog_bg"]}; dialog_button_bg: {tokens["dialog_button_bg"]}; danger: {tokens["danger"]}; form_panel_bg: {tokens["form_panel_bg"]}; table_error_bg: {tokens["table_error_bg"]}; table_warning_bg: {tokens["table_warning_bg"]}; selection_bg: {tokens["selection_bg"]}; selection_text: {tokens["selection_text"]}; selection_border: {tokens["selection_border"]}; selection_inactive_bg: {tokens["selection_inactive_bg"]}; */
    QMainWindow {{
        background: {tokens["window_bg"]};
        color: {tokens["text"]};
    }}
    QToolBar {{
        background: {tokens["toolbar_bg"]};
        border-bottom: 1px solid {tokens["border"]};
        spacing: 6px;
        padding: 4px 8px;
    }}
    QToolBar QToolButton {{
        color: {tokens["text"]};
        background: transparent;
        border: 1px solid transparent;
        border-radius: 4px;
        padding: 4px;
    }}
    QToolBar QToolButton:hover {{
        background: {tokens["hover_bg"]};
        border-color: {tokens["border"]};
    }}
    QToolBar QToolButton:checked, QToolBar QToolButton:pressed {{
        background: {tokens["active_bg"]};
        border-color: {tokens["accent"]};
        color: {tokens["accent"]};
    }}
    QToolBar QToolButton:disabled {{
        color: {tokens["disabled_text"]};
    }}
    QMenuBar {{
        color: {tokens["text"]};
        background: {tokens["toolbar_bg"]};
        border-bottom: 1px solid {tokens["border"]};
    }}
    QMenuBar::item {{
        color: {tokens["text"]};
        background: transparent;
        padding: 4px 10px;
    }}
    QMenuBar::item:selected {{
        background: {tokens["hover_bg"]};
    }}
    QMenu {{
        color: {tokens["text"]};
        background: {tokens["panel_bg"]};
        border: 1px solid {tokens["border"]};
    }}
    QMenu::item {{
        color: {tokens["text"]};
        padding: 5px 24px;
    }}
    QMenu::item:selected {{
        background: {tokens["hover_bg"]};
    }}
    QMenu::item:disabled {{
        color: {tokens["disabled_text"]};
    }}
    QToolTip {{
        color: {tokens["text"]};
        background: {tokens["panel_bg"]};
        border: 1px solid {tokens["border"]};
        padding: 4px;
    }}
    QDialog#xtable-message-dialog {{
        color: {tokens["text"]};
        background: {tokens["dialog_bg"]};
        border: 1px solid {tokens["border"]};
    }}
    QDialog#xtable-confirm-dialog {{
        color: {tokens["text"]};
        background: {tokens["dialog_bg"]};
        border: 1px solid {tokens["border"]};
    }}
    QFrame#message-dialog-icon-frame {{
        background: {tokens["active_bg"]};
        border: 1px solid {tokens["drawer_border"]};
        border-radius: 6px;
    }}
    QLabel#message-dialog-title {{
        color: {tokens["text"]};
        font-weight: 600;
        font-size: 14px;
    }}
    QLabel#message-dialog-body {{
        color: {tokens["muted"]};
        line-height: 150%;
    }}
    QDialogButtonBox QPushButton {{
        color: {tokens["text"]};
        background: {tokens["dialog_button_bg"]};
        border: 1px solid {tokens["border"]};
        border-radius: 4px;
        padding: 5px 14px;
        min-width: 64px;
    }}
    QDialogButtonBox QPushButton:hover {{
        background: {tokens["hover_bg"]};
        border-color: {tokens["accent"]};
    }}
    QDialogButtonBox QPushButton:focus {{
        border-color: {tokens["accent"]};
    }}
    QStatusBar {{
        color: {tokens["muted"]};
        background: {tokens["toolbar_bg"]};
        border-top: 1px solid {tokens["border"]};
    }}
    QWidget#status-left-group, QWidget#status-context-group, QWidget#status-state-group {{
        background: transparent;
    }}
    QWidget#status-context-group, QWidget#status-state-group {{
        border-left: 1px solid {tokens["shadow_border"]};
    }}
    QFrame#status-separator {{
        color: {tokens["shadow_border"]};
        background: {tokens["shadow_border"]};
        max-width: 1px;
    }}
    QStatusBar QLabel {{
        color: {tokens["muted"]};
        padding: 0 4px;
    }}
    QToolButton#status-issue-summary {{
        color: {tokens["text"]};
        background: transparent;
        border: 1px solid transparent;
        border-radius: 4px;
        padding: 2px 8px;
    }}
    QToolButton#status-issue-summary:hover {{
        background: {tokens["hover_bg"]};
        border-color: {tokens["drawer_border"]};
    }}
    QFrame#left-rail {{
        background: {tokens["panel_bg"]};
        border-right: 1px solid {tokens["border"]};
    }}
    QWidget#main-workspace {{
        background: {tokens["workspace_bg"]};
    }}
    QFrame#issue-drawer {{
        background: {tokens["panel_bg"]};
        border-top: 1px solid {tokens["drawer_border"]};
    }}
    QSplitter::handle {{
        background: {tokens["shadow_border"]};
        border-top: 1px solid {tokens["drawer_border"]};
        border-bottom: 1px solid {tokens["shadow_border"]};
        height: 4px;
    }}
    QWidget#diagnostics-page {{
        background: {tokens["panel_bg"]};
        color: {tokens["text"]};
    }}
    QTabWidget::pane {{
        background: {tokens["panel_bg"]};
        border: 1px solid {tokens["drawer_border"]};
        top: -1px;
    }}
    QTabBar::tab {{
        color: {tokens["muted"]};
        background: {tokens["toolbar_bg"]};
        border: 1px solid {tokens["border"]};
        padding: 5px 12px;
        min-width: 54px;
    }}
    QTabBar::tab:selected {{
        color: {tokens["text"]};
        background: {tokens["panel_bg"]};
        border-bottom-color: {tokens["panel_bg"]};
    }}
    QTabBar::tab:hover {{
        background: {tokens["hover_bg"]};
    }}
    QLineEdit {{
        color: {tokens["text"]};
        background: {tokens["workspace_bg"]};
        border: 1px solid {tokens["border"]};
        border-radius: 4px;
        padding: 4px 6px;
        selection-background-color: {tokens["selection_bg"]};
        selection-color: {tokens["selection_text"]};
    }}
    QLineEdit[active-editor="true"], QTextEdit[active-editor="true"] {{
        border-color: {tokens["accent"]};
        background: {tokens["workspace_bg"]};
    }}
    QLineEdit[display-mode="readonly"], QTextEdit[display-mode="readonly"] {{
        color: {tokens["muted"]};
        background: {tokens["panel_bg"]};
        border-color: {tokens["shadow_border"]};
    }}
    QComboBox {{
        color: {tokens["text"]};
        background: {tokens["workspace_bg"]};
        border: 1px solid {tokens["border"]};
        border-radius: 4px;
        padding: 4px 6px;
    }}
    QComboBox QAbstractItemView {{
        color: {tokens["text"]};
        background: {tokens["panel_bg"]};
        selection-background-color: {tokens["selection_bg"]};
        selection-color: {tokens["selection_text"]};
    }}
    QComboBox::drop-down {{
        border-left: 1px solid {tokens["border"]};
        width: 22px;
    }}
    QCheckBox {{
        color: {tokens["text"]};
        spacing: 8px;
    }}
    QTextEdit {{
        color: {tokens["text"]};
        background: {tokens["workspace_bg"]};
        border: 1px solid {tokens["border"]};
        border-radius: 4px;
        padding: 4px 6px;
        selection-background-color: {tokens["selection_bg"]};
        selection-color: {tokens["selection_text"]};
    }}
    QFrame#field-inspector {{
        background: {tokens["form_panel_bg"]};
        border-left: 1px solid {tokens["border"]};
    }}
    QFrame#field-editor-shell, QFrame[ui-kit-component="field-editor"] {{
        background: {tokens["form_panel_bg"]};
        border: 1px solid {tokens["border"]};
        border-radius: 6px;
    }}
    QFrame[field-state="invalid"] {{
        border-color: {tokens["danger"]};
        background: {tokens["table_error_bg"]};
    }}
    QFrame[field-state="disabled"], QFrame[field-state="readonly"] {{
        color: {tokens["disabled_text"]};
        background: {tokens["panel_bg"]};
    }}
    QToolButton[field-state="invalid"] {{
        color: {tokens["danger"]};
        border-color: {tokens["danger"]};
    }}
    QListWidget#data-list-view {{
        color: {tokens["text"]};
        background: {tokens["workspace_bg"]};
        border: 1px solid {tokens["border"]};
        selection-background-color: {tokens["selection_bg"]};
        selection-color: {tokens["selection_text"]};
    }}
    QTabWidget#workspace-tabs::pane {{
        border: 1px solid {tokens["drawer_border"]};
        background: {tokens["workspace_bg"]};
    }}
    QLabel#field-inspector-title {{
        color: {tokens["text"]};
        font-weight: 600;
    }}
    QToolButton#nav-table, QToolButton#nav-enum, QToolButton#nav-meta {{
        background: transparent;
        border: 1px solid transparent;
        border-radius: 5px;
        padding: 5px;
    }}
    QToolButton#nav-table:hover, QToolButton#nav-enum:hover, QToolButton#nav-meta:hover {{
        background: {tokens["hover_bg"]};
        border-color: {tokens["border"]};
    }}
    QToolButton#nav-table:checked, QToolButton#nav-enum:checked, QToolButton#nav-meta:checked {{
        background: {tokens["active_bg"]};
        border-color: {tokens["accent"]};
    }}
    QAbstractScrollArea {{
        color: {tokens["text"]};
        background: {tokens["workspace_bg"]};
        border: 1px solid {tokens["drawer_border"]};
    }}
    QTableWidget {{
        color: {tokens["text"]};
        background: {tokens["workspace_bg"]};
        alternate-background-color: {tokens["panel_bg"]};
        gridline-color: {tokens["drawer_border"]};
        selection-background-color: {tokens["selection_bg"]};
        selection-color: {tokens["selection_text"]};
    }}
    QTableWidget#preview-table {{
        border: 1px solid {tokens["drawer_border"]};
    }}
    QTableWidget::item[validation-state="error"] {{
        background: {tokens["table_error_bg"]};
    }}
    QTableWidget::item[validation-state="warning"] {{
        background: {tokens["table_warning_bg"]};
    }}
    QTableWidget::item:hover {{
        background: {tokens["hover_bg"]};
    }}
    QHeaderView::section {{
        color: {tokens["text"]};
        background: {tokens["toolbar_bg"]};
        border: 1px solid {tokens["border"]};
        padding: 4px;
    }}
    QTableCornerButton::section {{
        background: {tokens["toolbar_bg"]};
        border: 1px solid {tokens["border"]};
    }}
    QScrollBar {{
        background: {tokens["panel_bg"]};
        border: 1px solid {tokens["border"]};
    }}
    QScrollBar::handle {{
        background: {tokens["muted"]};
        border-radius: 3px;
    }}
    QLabel {{
        color: {tokens["text"]};
    }}
    QPushButton {{
        color: {tokens["text"]};
        background: {tokens["panel_bg"]};
        border: 1px solid {tokens["border"]};
        border-radius: 4px;
        padding: 4px;
    }}
    QPushButton:hover {{
        background: {tokens["hover_bg"]};
    }}
    QPushButton:checked {{
        border-color: {tokens["accent"]};
        color: {tokens["accent"]};
        background: {tokens["active_bg"]};
    }}
    QPushButton:disabled {{
        color: {tokens["disabled_text"]};
    }}
    QFrame#structure-editor {{
        background: {tokens["panel_bg"]};
        border-left: 1px solid {tokens["border"]};
    }}
    QFrame#table-explorer {{
        background: {tokens["panel_bg"]};
        border-right: 1px solid {tokens["border"]};
    }}
    QFrame#table-mode-bar {{
        background: {tokens["toolbar_bg"]};
        border-bottom: 1px solid {tokens["border"]};
    }}
    QFrame#inspector-panel {{
        background: {tokens["panel_bg"]};
        border-left: 1px solid {tokens["border"]};
    }}
    QLabel#inspector-panel-title {{
        color: {tokens["text"]};
        font-weight: 600;
        background: {tokens["toolbar_bg"]};
        border-bottom: 1px solid {tokens["border"]};
    }}
    QLabel#inspector-panel-empty {{
        color: {tokens["muted"]};
    }}
    QLabel#table-explorer-header, QLabel#structure-editor-params-label, QLabel#structure-editor-fields-label {{
        color: {tokens["text"]};
        font-weight: 600;
        padding: 2px 0;
    }}
    QToolButton#table-mode-data-button, QToolButton#table-mode-structure-button {{
        background: transparent;
        border: 1px solid transparent;
        border-radius: 3px;
        padding: 2px 10px;
        color: {tokens["text"]};
        font-size: 12px;
    }}
    QToolButton#table-mode-data-button:hover, QToolButton#table-mode-structure-button:hover {{
        background: {tokens["hover_bg"]};
        border-color: {tokens["border"]};
    }}
    QToolButton#table-mode-data-button:checked, QToolButton#table-mode-structure-button:checked {{
        background: {tokens["active_bg"]};
        border-color: {tokens["accent"]};
        color: {tokens["accent"]};
    }}
    QListWidget#table-explorer-list, QListWidget#structure-editor-field-list {{
        color: {tokens["text"]};
        background: {tokens["workspace_bg"]};
        border: 1px solid {tokens["border"]};
        selection-background-color: {tokens["selection_bg"]};
        selection-color: {tokens["selection_text"]};
    }}
    """
