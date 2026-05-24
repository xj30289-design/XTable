from __future__ import annotations

from PySide6.QtWidgets import QTabWidget, QWidget


class WorkspaceTabs(QTabWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("workspace-tabs")
        self.documents: dict[str, QWidget] = {}
        self.dirty: dict[str, bool] = {}
        self.active_document_key = ""
        self.document_count = 0
        self.setTabsClosable(True)
        self.currentChanged.connect(self._sync_active_from_index)

    def open_document(self, key: str, title: str, *, dirty: bool = False) -> None:
        page = QWidget()
        page.setObjectName(f"document-{key}")
        self.documents[key] = page
        self.dirty[key] = dirty
        self.addTab(page, self._title(title, dirty))
        self.document_count = len(self.documents)
        self.set_active_document(key)

    def set_active_document(self, key: str) -> None:
        page = self.documents[key]
        self.active_document_key = key
        self.setCurrentWidget(page)

    def close_document(self, key: str) -> bool:
        if self.dirty.get(key):
            self.setProperty("pending-close-document", key)
            return False
        self._remove_document(key)
        return True

    def confirm_pending_close(self) -> None:
        key = self.property("pending-close-document")
        if key:
            self._remove_document(str(key))
            self.setProperty("pending-close-document", "")

    def _remove_document(self, key: str) -> None:
        page = self.documents.pop(key)
        self.dirty.pop(key, None)
        index = self.indexOf(page)
        if index >= 0:
            self.removeTab(index)
        page.deleteLater()
        self.document_count = len(self.documents)
        self.active_document_key = next(iter(self.documents), "")

    def _sync_active_from_index(self, index: int) -> None:
        if index < 0:
            return
        widget = self.widget(index)
        for key, page in self.documents.items():
            if page is widget:
                self.active_document_key = key
                return

    @staticmethod
    def _title(title: str, dirty: bool) -> str:
        return f"{title}*" if dirty else title
