# XTable UI Kit 组件说明

本文档记录 Phase 1.5 UI Kit 的组件职责、状态、主题要求、objectName 和复用边界。后续新 UI 需求必须先进入 `xtable.ui` 实现为组件、页面、Dialog 或 Shell 能力，再由其他模块调用。

## EditorShell

- 路径：`src/xtable/ui/shell.py`
- 用途：统一编辑器窗口外壳，组合菜单、工具栏、导航、工作区、状态栏和底部诊断抽屉。
- objectName：调用方指定，Demo 使用 `ui-kit-demo-window`。
- 主要方法：`show_page(key)`、`apply_theme(theme)`、`open_diagnostics(tab)`、`update_issue_summary(errors, warnings, infos)`。
- 焦点：内置 `focus_manager`，窗口初始化时安装 `EditorFocusEventFilter`；页面切换和非输入区域点击会主动失活当前输入控件。
- 复用限制：不读取项目文件，不保存配置，不生成校验结果；业务动作必须通过 handler 或服务注入。

## EditorToolbar

- 路径：`src/xtable/ui/components/toolbar.py`
- 用途：按分组展示高频图标 action，并把全局 action 推到右侧。
- objectName：`editor-toolbar`，右侧 spacer 为 `toolbar-right-spacer`。
- 主题要求：action 必须设置 `icon-id`，由 `icon_for` 随主题刷新。
- 复用限制：不实现保存、导入、导出、校验等业务行为。

## NavigationRail

- 路径：`src/xtable/ui/components/navigation.py`
- 用途：承载组件实验室页面或业务页面主导航。
- objectName：`navigation-rail`，按钮为 `nav-{key}`。
- 状态：checked 表示当前页。
- 复用限制：只发出页面选择，不创建中央页面内容。

## IconToolButton

- 路径：`src/xtable/ui/components/buttons.py`
- 用途：统一图标按钮尺寸、tooltip、accessibleName、icon-id 和主题刷新。
- objectName：`icon-tool-button-{icon_id}`。
- 复用限制：只处理视觉和可访问性，不决定业务语义。

## EditorStatusBar

- 路径：`src/xtable/ui/status_bar.py`
- 用途：展示问题摘要、项目上下文、当前对象、保存状态、校验状态和后台任务。
- objectName：`status-bar`；问题摘要为 `status-issue-summary`。
- 状态：`update_issue_summary(errors, warnings, infos, theme)`。
- 复用限制：不计算问题数量，不执行校验。

## DiagnosticsDrawer

- 路径：`src/xtable/ui/issue_drawer.py`
- 用途：底部承载问题、日志和后续诊断信息。
- objectName：`issue-drawer`；页签为 `diagnostics-tabs`。
- 状态：通过 `EditorShell.open_diagnostics("issues" | "logs")` 控制打开和页签。
- 复用限制：不生成问题和日志，只展示数据。

## MessageDialog / ConfirmDialog

- 路径：`src/xtable/ui/dialogs.py`
- 用途：统一错误、信息和确认弹窗。
- objectName：`xtable-message-dialog`、`xtable-confirm-dialog`。
- 状态：`dialog-kind` 区分 `error`、`info`、`confirm`。
- 复用限制：禁止业务模块直接使用 `QMessageBox` 或裸 `QDialog` 作为最终 UI。

## PreviewTable

- 路径：`src/xtable/ui/components/tables.py`
- 用途：表格 UI 样板，展示普通、只读、错误、警告和 dirty 状态，并提供 UI Kit 级选区、粘贴和批量填充契约。
- objectName：`preview-table`。
- 状态：`set_demo_state("normal" | "dirty" | "error" | "warning")`。
- 交互：`paste_tsv(text)` 支持多行多列粘贴；`batch_fill(value)` 支持选区批量填充；`copy_selection()` 输出 TSV；`keyPressEvent` 支持 `Ctrl+C` 和 `Ctrl+V`；只读单元格拒绝写入并设置 `last-rejected-write=readonly`。
- Demo 入口：Tables 页面提供复制、粘贴、批量填充图标按钮，作为业务层调用表格能力的 UI 样板。
- 滚动：默认启用 `ScrollPerPixel`，用于连续滚动体验。
- 复用限制：当前仍是静态 `QTableWidget` 样板，不替代 Phase 3 的真实 `QAbstractTableModel`。

## FieldInspector

- 路径：`src/xtable/ui/components/inspector.py`
- 用途：字段属性面板样板，展示字段名、类型、必填、默认值和说明。
- objectName：`field-inspector`。
- 状态：`set_field_state("normal" | "invalid" | "readonly" | "disabled")`。
- 输入区分：editable 输入框使用 active editor 焦点环；readonly 状态使用 `setReadOnly(True)` 和 `display-mode=readonly`；disabled 状态禁用但保持可读。
- 复用限制：不校验真实字段规则，不写回领域模型。

## Field Editor Shells

- 路径：`src/xtable/ui/components/inspector.py`
- 组件：`PickerShell`、`JsonEditorShell`、`ListEditorShell`、`MetaEditorShell`。
- 用途：为 Enum、Reference、Json、List、Meta 字段编辑提供入口样板。
- objectName：`enum-picker-shell`、`reference-picker-shell`、`json-editor-shell`、`list-editor-shell`、`meta-editor-shell`。
- 状态：`field-state` 支持 `normal`、`invalid`、`readonly`、`disabled`、`empty`。
- Picker：内置状态按钮，objectName 为 `{kind}-picker-status-button`，通过图标区分 normal、invalid、readonly、disabled。
- Json：`JsonEditorShell` 提供可见校验、格式化、压缩图标按钮，按钮 objectName 为 `json-editor-validate-button`、`json-editor-format-button`、`json-editor-minify-button`；API 为 `validate_json()`、`format_json()`、`minify_json()`；`json-editor-status` 随光标移动展示行列，并在校验失败时展示错误行列。
- 只读/display：`JsonEditorShell`、`MetaEditorShell`、`PickerShell`、`ListEditorShell` 按状态设置 `display-mode`，真实可编辑控件和只读/展示控件必须可通过属性区分。
- 复用限制：当前为 UI Shell，不负责业务校验、引用解析或列表写回。

## WorkspaceTabs

- 路径：`src/xtable/ui/components/workspace.py`
- 用途：工作区多文档页签样板，表达 active document、dirty 标记、关闭确认和页签切换。
- objectName：`workspace-tabs`。
- 主要方法：`open_document(key, title, dirty)`、`set_active_document(key)`、`close_document(key)`、`confirm_pending_close()`。
- 复用限制：不保存真实文档，只维护 UI 层页签状态。

## DataListView

- 路径：`src/xtable/ui/components/data_list.py`
- 用途：资源列表/数据列表样板，支持筛选、选择、加载态、空态、状态徽标文字。
- objectName：`data-list-view`；筛选输入为 `data-list-filter`。
- 视觉：筛选输入固定显示在列表顶部，列表内容区域下移，避免只有逻辑没有可见入口。
- 主要方法：`apply_filter(text)`、`set_loading(loading)`、`set_empty()`。
- 复用限制：不读取项目目录，不解析真实资源文件。

## EditorFocusManager

- 路径：`src/xtable/ui/focus.py`
- 用途：维护唯一 active editor，提供激活和外部点击失活的基础契约。
- 组件：`EditorFocusManager`、`ManagedLineEdit`、`EditorFocusEventFilter`。
- 主要方法：`activate(editor)`、`deactivate_active(reason)`。
- 安装入口：`install_editor_focus_management(root, manager)` 会给根窗口和现有 `QLineEdit`/`QTextEdit` 安装事件过滤器。
- 复用限制：当前覆盖文本输入类控件；后续真实表格单元格编辑器需要接入同一接口或安装到编辑器 widget 上。

## UiKitDemoWindow

- 路径：`src/xtable/ui/demo.py`
- 用途：独立 UI Kit 实验室。
- objectName：`ui-kit-demo-window`。
- 页面：Overview、Theme Lab、Buttons & Icons、Dialogs、Diagnostics、Tables、Forms、Layouts、Table、Enum、Meta。
- 控制区：`demo-control-panel`，可调错误/警告/信息数量、抽屉高度、表格状态和字段状态。
- 复用限制：Demo 使用静态数据，不连接真实项目服务。
