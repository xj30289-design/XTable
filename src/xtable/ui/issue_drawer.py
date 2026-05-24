from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QTableWidget, QTabWidget, QVBoxLayout, QWidget


class IssueDrawer(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("issue-drawer")
        self.setProperty("drawer-position", "bottom")
        self.setMinimumHeight(180)
        self.setMaximumHeight(260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        tabs = QTabWidget()
        tabs.setObjectName("diagnostics-tabs")
        tabs.addTab(self._build_issue_page(), "问题")
        tabs.addTab(self._build_log_page(), "日志")
        layout.addWidget(tabs)
        self.hide()

    def _build_issue_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("diagnostics-page")
        layout = QVBoxLayout(page)
        table = QTableWidget(0, 5)
        table.setObjectName("issue-table")
        table.setHorizontalHeaderLabels(["级别", "对象", "位置", "原因", "建议"])
        layout.addWidget(table)
        return page

    def _build_log_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("diagnostics-page")
        layout = QVBoxLayout(page)
        filters = QHBoxLayout()
        filters.addWidget(QLabel("级别"))
        search = QLineEdit()
        search.setObjectName("log-search")
        search.setPlaceholderText("搜索日志")
        filters.addWidget(search)
        table = QTableWidget(0, 4)
        table.setObjectName("log-table")
        table.setHorizontalHeaderLabels(["时间", "级别", "模块", "内容"])
        layout.addLayout(filters)
        layout.addWidget(table)
        return page
