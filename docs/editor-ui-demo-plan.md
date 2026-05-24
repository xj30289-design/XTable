# XTable Editor UI Demo 规划文档

本文档是 XTable 项目 UI 基座建设规划，用于在继续推进核心数据模型和业务编辑功能之前，先完成一套独立、可组合、可切换主题、可自由调整窗口布局的编辑器 UI Demo。后续正式业务页面必须优先复用该 UI 模块，避免继续出现主题不一致、系统默认控件露出、弹窗样式割裂、图标风格不统一等问题。

当前会话角色为测试角色。本文档只定义目标、组件范围、验收标准和开发顺序；实际代码、测试和资源实现由开发角色在开发会话执行。

## 1. 建设目标

Editor UI Demo 的目标不是做业务功能，而是先沉淀一套稳定 UI Kit：

- 所有编辑器常用窗口、面板、弹窗、按钮、状态栏、抽屉和图标都能独立展示。
- 所有组件都支持 Light/Dark 两套主题，不能依赖 Qt 默认浅色样式。
- 所有组件都能在 Demo 中自由组合、切换状态、切换主题、调整窗口大小。
- UI 模块内部维护自己的功能文档、组件说明、状态说明和验收清单。
- 业务模块不能直接裸用复杂 Qt 控件，应优先使用 UI Kit 提供的封装组件。

## 2. 模块定位

建议将 UI 模块拆成两层：

| 层级 | 目标 | 示例 |
| --- | --- | --- |
| UI Kit | 提供可复用基础组件，不依赖业务数据模型 | 图标按钮、状态栏字段、诊断抽屉、消息弹窗、主题 token、表格外观 |
| Editor UI Demo | 展示和验证 UI Kit 组合效果 | 主窗口 Demo、弹窗 Demo、表格 Demo、状态栏 Demo、主题切换 Demo |

UI Kit 可以依赖 PySide6/Qt，但不得依赖 `domain`、`application`、`io`、`validation` 的业务实现。Demo 可以使用假数据模拟项目、表格、问题、日志和状态。

## 3. 建议目录结构

```text
src/xtable/ui/
  kit/
    theme.py               # 主题 token、状态 token、尺寸 token
    icons.py               # icon id、主题着色、资源加载
    actions.py             # action 规范、菜单/工具栏动作定义
    buttons.py             # 图标按钮、分段按钮、状态按钮
    dialogs.py             # 统一消息/确认/输入弹窗
    status_bar.py          # 状态栏分组、问题摘要、任务状态
    drawer.py              # 底部诊断抽屉、可拖拽容器
    panels.py              # 侧栏、面板、空状态、属性面板
    tables.py              # 表格外观、header、选择态、空表格
    inputs.py              # 输入框、下拉、搜索、筛选、数值控件
  demo/
    main.py                # Demo 启动入口
    demo_window.py         # Demo 主窗口
    pages/                 # 各组件展示页
  resources/
    icons/
docs/
  editor-ui-demo-plan.md
  ui-implementation-guidelines.md
  ui-icon-guidelines.md
```

如果开发角色认为当前代码量暂时不需要 `kit/` 子目录，也可以先保留 `src/xtable/ui/` 平铺结构，但必须保证组件边界清晰，并在文档中说明迁移路径。

## 4. 组件清单

### 4.1 应用框架组件

| 组件 | 用途 | 必须支持的状态 |
| --- | --- | --- |
| `EditorMainWindow` | 编辑器主窗口骨架 | Light/Dark、最大化、小窗口、空项目、已打开项目 |
| `EditorMenuBar` | 文件、编辑、查看、窗口、帮助菜单 | hover、disabled、快捷键、子菜单 |
| `EditorToolBar` | 高频图标操作区 | 分组、靠右全局按钮、disabled、hover、pressed |
| `LeftRail` | Table/Enum/Meta 等主导航 | selected、hover、disabled、tooltip |
| `WorkspaceTabs` | 多页面工作区 | active、dirty、closeable、empty |
| `BottomStatusBar` | 底部状态信息 | 左侧问题摘要、中间上下文、右侧任务/保存/校验 |
| `DiagnosticDrawer` | 底部问题和日志抽屉 | collapsed、expanded、resizable、问题页、日志页 |

### 4.2 通用按钮与操作组件

| 组件 | 用途 | 必须支持的状态 |
| --- | --- | --- |
| `IconButton` | 工具栏和侧栏图标按钮 | normal、hover、pressed、checked、disabled |
| `ActionButton` | 明确命令按钮 | primary、secondary、danger、disabled |
| `SegmentedControl` | 模式切换 | selected、hover、disabled |
| `IssueSummaryButton` | 问题摘要入口 | error/warn/info/ok、数量变化、tooltip |
| `ThemeToggleButton` | 主题切换 | Light、Dark |
| `ToolbarSeparator` | 工具栏分隔 | Light/Dark 低对比分隔线 |

### 4.3 编辑器表格组件

| 组件 | 用途 | 必须支持的状态 |
| --- | --- | --- |
| `EditorTableView` | 核心表格视图外观 | 空表、选区、hover、readonly、dirty、error、warning |
| `TableHeader` | 表头样式 | sort、filter、required、primary key、feature key |
| `CellBadge` | 单元格状态标记 | error、warn、readonly、reference、deprecated |
| `InlineEditorShell` | 单元格编辑容器 | focus、invalid、readonly |
| `TableEmptyState` | 空表占位 | 无项目、无表格、无数据 |
| `SelectionInfo` | 当前选区信息 | 单格、多格、整行、整列 |

### 4.4 字段与属性编辑组件

| 组件 | 用途 | 必须支持的状态 |
| --- | --- | --- |
| `PropertyPanel` | 表、字段、枚举、Meta 属性编辑 | empty、readonly、dirty、invalid |
| `TextField` | 文本输入 | focus、disabled、error、warning |
| `NumberField` | 数字输入 | min/max、step、invalid |
| `ComboField` | 下拉选择 | empty、search、disabled |
| `CheckboxField` | 布尔值 | checked、unchecked、mixed、disabled |
| `EnumPicker` | 枚举选择 | valid、missing、deprecated |
| `ReferencePicker` | 跨表引用选择 | valid、missing、broken |
| `JsonEditorShell` | Json 编辑入口 | valid、invalid、formatted、collapsed |
| `ListEditorShell` | 列表字段编辑入口 | empty、nested、invalid |
| `MetaEditorShell` | Meta 复合字段编辑入口 | collapsed、expanded、invalid |

### 4.5 反馈与弹窗组件

| 组件 | 用途 | 必须支持的状态 |
| --- | --- | --- |
| `MessageDialog` | 信息、错误、警告提示 | info、warning、error、success |
| `ConfirmDialog` | 确认操作 | default、danger、cancel |
| `InputDialog` | 简单输入 | focus、invalid、empty |
| `ProjectDialog` | 新建/打开项目 | valid、invalid、path missing |
| `Toast` | 短反馈 | info、success、warning、error |
| `InlineMessage` | 表单内提示 | info、warning、error |

弹窗必须完全替代裸 `QMessageBox`。所有弹窗都必须使用项目主题、项目图标、项目按钮样式和统一间距。

### 4.6 诊断组件

| 组件 | 用途 | 必须支持的状态 |
| --- | --- | --- |
| `IssueTable` | 问题列表 | error、warn、info、empty、selected |
| `IssueFilterBar` | 问题筛选 | level、object、keyword |
| `IssueDetailPanel` | 问题详情和建议 | collapsed、expanded |
| `LogTable` | 日志列表 | debug、info、warn、error、empty |
| `LogFilterBar` | 日志筛选 | level、keyword、time range |
| `DiagnosticsCopyButton` | 复制诊断信息 | copied、failed |

### 4.7 布局与窗口组件

| 组件 | 用途 | 必须支持的状态 |
| --- | --- | --- |
| `ResizableSplitter` | 可拖拽分割布局 | horizontal、vertical、collapsed |
| `DockPanelShell` | 可停靠面板候选 | docked、floating、hidden |
| `PanelHeader` | 面板标题栏 | icon、title、actions |
| `SearchBar` | 搜索入口 | empty、typing、clearable |
| `FilterBar` | 筛选栏 | active filters、clear all |
| `EmptyState` | 空状态组件 | icon、title、description、action |

## 5. 主题系统要求

主题系统必须从“补 QSS”升级为 token 驱动：

| Token 类别 | 示例 |
| --- | --- |
| 颜色 | `window_bg`、`panel_bg`、`workspace_bg`、`toolbar_bg`、`text`、`muted`、`border`、`drawer_border`、`focus_ring`、`selection_bg` |
| 语义色 | `info`、`success`、`warning`、`error`、`danger` |
| 状态色 | `hover_bg`、`active_bg`、`pressed_bg`、`disabled_text` |
| 间距 | `space_2`、`space_4`、`space_8`、`space_12`、`space_16` |
| 尺寸 | `toolbar_icon`、`sidebar_icon`、`status_icon`、`button_height`、`statusbar_height` |
| 边框 | `radius_sm`、`radius_md`、`border_width`、`splitter_handle_width` |

主题验收必须覆盖：

- 主窗口。
- 菜单栏和菜单。
- 工具栏。
- 左侧栏。
- 表格和表头。
- 状态栏。
- 诊断抽屉。
- 所有弹窗。
- 输入控件。
- 滚动条。
- disabled、hover、checked、selected、focus 状态。

## 6. UIDemo 页面设计

Editor UI Demo 至少包含以下页面：

| Demo 页面 | 展示内容 |
| --- | --- |
| Overview | 主窗口、菜单、工具栏、侧栏、状态栏、诊断抽屉组合态 |
| Theme Lab | Light/Dark 切换，所有 token 色块和状态色 |
| Buttons & Icons | 所有图标按钮、普通按钮、危险按钮、分段按钮、禁用态 |
| Dialogs | 信息、警告、错误、确认、输入、项目弹窗 |
| Status Bar | 项目状态、保存状态、校验状态、任务状态、问题摘要 |
| Diagnostics | 问题列表、日志列表、筛选、详情、复制诊断信息 |
| Tables | 空表、普通表、选区、错误单元格、警告单元格、只读单元格 |
| Forms | 文本、数字、下拉、枚举、引用、Json、List、Meta 编辑入口 |
| Layouts | splitter、抽屉、高度记忆、侧栏折叠、小窗口适配 |

每个页面都必须能在不打开真实项目的情况下运行，并使用假数据驱动。

## 7. 组合场景

Demo 需要覆盖以下真实编辑器组合场景：

1. 空项目状态：无项目打开，所有业务操作 disabled，提示用户新建或打开项目。
2. 已打开项目：状态栏展示项目名、当前对象、保存状态、校验状态。
3. 表格编辑中：工具栏撤销/重做可用，状态栏显示未保存。
4. 校验有问题：状态栏左侧显示错误/警告数量，点击打开问题抽屉。
5. 日志查看：底部抽屉切换到日志页，可筛选和搜索。
6. 保存失败：显示项目风格错误弹窗，不能使用系统默认 QMessageBox。
7. 小窗口：主窗口缩小时，文本不能重叠，状态栏和工具栏能合理收缩。
8. Dark 主题：所有区域无默认白底、默认系统按钮或不协调边界。

## 8. 禁止事项

- 禁止业务 UI 直接使用裸 `QMessageBox`。
- 禁止业务 UI 直接创建未封装的复杂 Qt 复合控件作为最终界面。
- 禁止在业务 UI 中硬编码颜色、边框、字号、间距和图标路径。
- 禁止使用临时文本符号代替图标。
- 禁止只在 Light 主题验收组件。
- 禁止只用“控件存在”测试代替视觉和主题验收。
- 禁止新增 UI 组件但不补 Demo 页面和截图验收。

## 9. 验收标准

Editor UI Demo 完成后，必须满足：

- Demo 可独立启动，不依赖真实项目数据。
- Light/Dark 主题可一键切换。
- 所有组件在 Demo 中可见，关键状态可手动切换或通过假数据触发。
- 所有图标来自统一 icon id 和 icon loader。
- 所有弹窗来自统一 Dialog 服务。
- 主窗口、弹窗、诊断抽屉、表格、状态栏都有 Light/Dark 截图验收。
- 自动化测试覆盖组件 objectName、icon-id、主题 stylesheet 关键 selector、状态栏布局、诊断抽屉、弹窗服务。
- 评估文档中第五批次 `B5-001`、`B5-002` 可以据此关闭。

## 10. 建议开发顺序

1. UI Token 与主题系统：补齐 token 分类、QSS 生成、Light/Dark 基础覆盖。
2. 图标与按钮基座：统一 icon id、按钮状态、工具栏/侧栏按钮。
3. Dialog 服务：替代裸 `QMessageBox`，完成错误/警告/确认/输入弹窗。
4. 主窗口骨架 Demo：菜单、工具栏、侧栏、工作区、状态栏、诊断抽屉。
5. 状态栏与诊断组件：问题摘要、日志页、问题页、筛选和详情占位。
6. 表格外观 Demo：表头、选区、错误/警告/只读状态、空表。
7. 表单与字段编辑入口 Demo：Json/List/Meta/Enum/Reference 等入口外观。
8. 布局能力：窗口缩放、splitter、抽屉高度记忆、侧栏折叠。
9. 截图验收与文档补齐：Light/Dark 全页面截图、组件说明和验收清单。

## 11. 对后续阶段的影响

在 Editor UI Demo 完成前，建议暂停新增复杂业务 UI 页面。Phase 2 可以继续推进纯业务模型和非 UI 测试，但 Phase 3 表格编辑工作台不应绕过 UI Kit 直接实现最终界面。

后续阶段使用规则：

- Phase 3 表格编辑工作台必须复用 `EditorTableView`、`BottomStatusBar`、`DiagnosticDrawer`、`MessageDialog`。
- Phase 4 校验系统必须复用 `IssueSummaryButton`、`IssueTable`、`IssueDetailPanel`。
- Phase 5 导入导出必须复用 `MessageDialog`、`ConfirmDialog`、`Progress/Task` 状态组件。
- Phase 6 Enum/Meta 必须复用 `PropertyPanel`、`EnumPicker`、`MetaEditorShell`。
- Phase 7 日志诊断必须复用 `DiagnosticDrawer`、`LogTable`、`LogFilterBar`。

## 12. 文档维护要求

UI 模块内部必须维护功能文档：

- 每个组件说明用途、状态、依赖、主题 token 和验收方式。
- 每个 Demo 页面说明可切换状态和对应验收点。
- 每次新增 UI 组件，必须同步更新本文档或拆分后的组件文档。
- 每次发现 UI 主题、图标、弹窗或布局问题，必须回写 [UI 实现质量规范](./ui-implementation-guidelines.md)。

## 13. 当前未关闭问题映射

| 问题 | 本规划中的关闭路径 |
| --- | --- |
| `B5-001` 提示弹窗不符合项目 UI 规范 | 通过统一 Dialog 服务、Dialog Demo 页面和 Light/Dark 弹窗截图验收关闭 |
| `B5-002` UI 主题问题反复出现 | 通过 UI Kit、主题 token、组件封装、Demo 页面和截图回归治理关闭 |
