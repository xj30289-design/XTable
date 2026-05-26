from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QSlider,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from xtable.ui.components import (
    DataListView,
    FieldInspector,
    IconToolButton,
    JsonEditorShell,
    ListEditorShell,
    MetaEditorShell,
    PickerShell,
    PreviewTable,
    TableWorkbench,
    WorkspaceTabs,
)
from xtable.ui.dialogs import ConfirmDialog, MessageDialog
from xtable.ui.icons import icon_for
from xtable.ui.shell import EditorShell, make_placeholder_page


class UiKitDemoWindow(EditorShell):
    def __init__(self) -> None:
        self.preview_table = PreviewTable()
        self.field_inspector = FieldInspector()
        super().__init__(
            title="XTable UI Kit Demo",
            pages=[
                ("overview", "Overview", "diagnostics", self._build_overview_page()),
                ("theme-lab", "Theme Lab", "theme", self._build_theme_lab_page()),
                ("buttons-icons", "Buttons & Icons", "project-save", self._build_buttons_page()),
                ("dialogs", "Dialogs", "info", self._build_dialogs_page()),
                ("diagnostics", "Diagnostics", "issues", self._build_diagnostics_page()),
                ("tables", "Tables", "table", self._build_tables_page()),
                ("forms", "Forms", "meta", self._build_forms_page()),
                ("layouts", "Layouts", "diagnostics", self._build_layouts_page()),
                ("table", "Table", "table", self._build_table_page()),
                ("enum", "Enum", "enum", self._build_enum_page()),
                ("meta", "Meta", "meta", self._build_meta_page()),
            ],
            handlers={
                "action-new-project": self.show_error_preview,
                "action-open-project": self.show_confirm_preview,
                "action-save-project": self.show_error_preview,
                "action-open-ui-kit-demo": lambda: None,
            },
            object_name="ui-kit-demo-window",
        )
        self.update_issue_summary(2, 4, 1)

    def _build_control_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("demo-control-panel")
        layout = QGridLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.errors_input = QSpinBox()
        self.errors_input.setObjectName("demo-errors-input")
        self.errors_input.setRange(0, 99)
        self.errors_input.setValue(2)
        self.warnings_input = QSpinBox()
        self.warnings_input.setObjectName("demo-warnings-input")
        self.warnings_input.setRange(0, 99)
        self.warnings_input.setValue(4)
        self.infos_input = QSpinBox()
        self.infos_input.setObjectName("demo-infos-input")
        self.infos_input.setRange(0, 99)
        self.infos_input.setValue(1)
        for spin in (self.errors_input, self.warnings_input, self.infos_input):
            spin.valueChanged.connect(self._sync_issue_counts)

        self.drawer_height_input = QSlider()
        self.drawer_height_input.setObjectName("demo-drawer-height-input")
        self.drawer_height_input.setRange(160, 360)
        self.drawer_height_input.setValue(220)
        self.drawer_height_input.valueChanged.connect(self._sync_drawer_height)

        self.table_state_input = QComboBox()
        self.table_state_input.setObjectName("demo-table-state-input")
        self.table_state_input.addItems(["normal", "dirty", "error", "warning"])
        self.table_state_input.currentTextChanged.connect(self.preview_table.set_demo_state)

        self.field_state_input = QComboBox()
        self.field_state_input.setObjectName("demo-field-state-input")
        self.field_state_input.addItems(["normal", "invalid", "readonly", "disabled"])
        self.field_state_input.currentTextChanged.connect(self.field_inspector.set_field_state)

        widgets = [
            ("错误", self.errors_input),
            ("警告", self.warnings_input),
            ("信息", self.infos_input),
            ("抽屉高度", self.drawer_height_input),
            ("表格状态", self.table_state_input),
            ("字段状态", self.field_state_input),
        ]
        for row, (label, widget) in enumerate(widgets):
            layout.addWidget(QLabel(label), row, 0)
            layout.addWidget(widget, row, 1)
        return panel

    def _sync_issue_counts(self) -> None:
        self.update_issue_summary(
            self.errors_input.value(),
            self.warnings_input.value(),
            self.infos_input.value(),
        )

    def _sync_drawer_height(self, height: int) -> None:
        self.open_diagnostics("issues")
        self.issue_drawer.setMinimumHeight(160)
        self.issue_drawer.setMaximumHeight(380)
        total_height = max(self.main_splitter.height(), height + 1)
        self.main_splitter.setSizes([total_height - height, height])

    def _make_lab_page(self, title: str, body: QWidget | None = None) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title_label = QLabel(title)
        title_label.setObjectName("demo-page-title")
        layout.addWidget(title_label)
        layout.addWidget(self._build_control_panel())
        if body is not None:
            layout.addWidget(body, 1)
        else:
            layout.addWidget(QLabel("UI Kit 状态实验页面"), 1)
        return page

    def _build_overview_page(self) -> QWidget:
        return self._make_lab_page("Overview")

    def _build_theme_lab_page(self) -> QWidget:
        return self._make_lab_page("Theme Lab")

    def _build_buttons_page(self) -> QWidget:
        return self._make_lab_page("Buttons & Icons")

    def _build_dialogs_page(self) -> QWidget:
        body = QWidget()
        layout = QHBoxLayout(body)
        error_button = IconToolButton("error", "错误弹窗")
        error_button.setObjectName("demo-error-dialog-button")
        error_button.clicked.connect(self.show_error_preview)
        confirm_button = IconToolButton("ok", "确认弹窗")
        confirm_button.setObjectName("demo-confirm-dialog-button")
        confirm_button.clicked.connect(self.show_confirm_preview)
        layout.addWidget(error_button)
        layout.addWidget(confirm_button)
        layout.addStretch()
        return self._make_lab_page("Dialogs", body)

    def _build_diagnostics_page(self) -> QWidget:
        return self._make_lab_page(
            "Diagnostics",
            DataListView(
                [
                    ("errors", "错误列表", "diagnostics", "error"),
                    ("warnings", "警告列表", "diagnostics", "warning"),
                    ("logs", "运行日志", "logs", "ok"),
                ]
            ),
        )

    def _build_tables_page(self) -> QWidget:
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        toolbar = QHBoxLayout()
        fill_input = QLineEdit("批量值")
        fill_input.setObjectName("table-batch-fill-input")
        copy_button = QToolButton()
        copy_button.setObjectName("table-copy-selection-button")
        copy_button.setIcon(icon_for("export"))
        copy_button.setToolTip("复制选区")
        paste_button = QToolButton()
        paste_button.setObjectName("table-paste-selection-button")
        paste_button.setIcon(icon_for("import"))
        paste_button.setToolTip("从剪贴板粘贴")
        fill_button = QToolButton()
        fill_button.setObjectName("table-batch-fill-button")
        fill_button.setIcon(icon_for("validate"))
        fill_button.setToolTip("批量填充选区")
        self.preview_table.setRowCount(32)
        self.preview_table.setColumnCount(10)
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(self.preview_table.copy_selection()))
        paste_button.clicked.connect(lambda: self.preview_table.paste_tsv(QApplication.clipboard().text()))
        fill_button.clicked.connect(lambda: self.preview_table.batch_fill(fill_input.text()))
        toolbar.addWidget(fill_input)
        toolbar.addWidget(copy_button)
        toolbar.addWidget(paste_button)
        toolbar.addWidget(fill_button)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        layout.addWidget(self.preview_table, 1)
        return self._make_lab_page("Tables", body)

    def _build_forms_page(self) -> QWidget:
        body = QWidget()
        layout = QGridLayout(body)
        layout.addWidget(PickerShell("enum", "EnumPicker", ["Common", "Rare", "Epic"]), 0, 0)
        layout.addWidget(
            PickerShell("reference", "ReferencePicker", ["items.item_id", "skills.skill_id"]),
            0,
            1,
        )
        layout.addWidget(JsonEditorShell(state="invalid"), 1, 0)
        layout.addWidget(ListEditorShell(state="empty"), 1, 1)
        layout.addWidget(PickerShell("readonly-enum", "ReadonlyPicker", ["Locked"], state="readonly"), 2, 0)
        layout.addWidget(MetaEditorShell(state="readonly"), 2, 1)
        layout.addWidget(MetaEditorShell(state="disabled"), 3, 0, 1, 2)
        return self._make_lab_page("Forms", body)

    def _build_layouts_page(self) -> QWidget:
        tabs = WorkspaceTabs()
        tabs.open_document("items", "Items", dirty=True)
        tabs.open_document("skills", "Skills", dirty=False)
        tabs.open_document("qualities", "Qualities", dirty=False)
        return self._make_lab_page("Layouts", tabs)

    def _build_table_page(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(TableWorkbench(), 1)
        layout.addWidget(self.field_inspector)
        return page

    def _build_enum_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 18, 18, 18)
        title = QLabel("枚举样板")
        title.setObjectName("demo-page-title")
        values = QListWidget()
        values.setObjectName("enum-preview-list")
        values.addItems(["Common = 1", "Rare = 2", "Epic = 3", "Legendary = 4"])
        layout.addWidget(title)
        layout.addWidget(values)
        layout.addWidget(
            DataListView(
                [
                    ("items", "Items", "table", "dirty"),
                    ("skills", "Skills", "table", "ok"),
                    ("qualities", "Qualities", "enum", "warning"),
                ]
            )
        )
        return page

    def _build_meta_page(self) -> QWidget:
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.addWidget(make_placeholder_page("Meta 结构字段样板"))
        layout.addWidget(JsonEditorShell(state="normal"))
        return body

    def show_error_preview(self) -> None:
        MessageDialog.error(
            "保存失败",
            "这是 UI Kit Demo 的错误弹窗样板。",
            theme=self.property("theme") or "light",
            parent=self,
        ).exec()

    def show_confirm_preview(self) -> None:
        ConfirmDialog(
            "覆盖文件",
            "确认覆盖当前导出文件？",
            theme=self.property("theme") or "light",
            parent=self,
        ).exec()


def create_demo_window() -> UiKitDemoWindow:
    configure_ui_font(QApplication.instance())
    return UiKitDemoWindow()


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    configure_ui_font(app)
    window = create_demo_window()
    window.show()
    return app.exec()


def configure_ui_font(app: QApplication | None) -> None:
    if app is None:
        return
    for font_path in (
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/msyh.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
        Path("C:/Windows/Fonts/simsun.ttf"),
    ):
        if font_path.exists():
            QFontDatabase.addApplicationFont(str(font_path))
    preferred = [
        "Microsoft YaHei UI",
        "Microsoft YaHei",
        "SimSun",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "Arial Unicode MS",
    ]
    available = set(QFontDatabase.families())
    for family in preferred:
        if family in available:
            app.setFont(QFont(family, 9))
            return


if __name__ == "__main__":
    raise SystemExit(main())
