# XTable UI 实现质量规范

本文档是 XTable 项目规范的一部分，用于约束后续 UI 开发、评审和验收。凡涉及工具栏、侧边栏、状态栏、主题、诊断抽屉、图标按钮或通用面板的改动，都必须同步对照本规范。

## 1. 重复问题防线

第三批次与第五批次验收确认以下问题已重复出现，后续不得只做局部修补：

- 主题样式不能只覆盖外层容器。新增 Qt 组件时，必须同时覆盖其子控件、viewport、pane、tab、header、corner、selection、disabled、hover、checked 和 scrollbar 状态。
- 图标按钮不能使用 Qt 默认图标、临时文本符号或单次截图里“看起来能用”的占位图标。所有图标必须进入统一 icon id、统一加载器和主题着色流程。
- 诊断类入口不能分散在多个主入口里。问题、日志、诊断信息统一归入底部诊断抽屉；状态栏承载高频状态入口，菜单承载低频命令。
- 禁止业务界面裸用系统弹窗。错误、警告、确认、删除、覆盖、退出等提示必须通过统一 Dialog 服务或封装组件创建，不得直接调用 `QMessageBox` 作为最终 UI。
- 自动化测试不能只验证控件存在或 stylesheet 包含字符串。主题、布局和图标类问题必须有运行时属性检查，并补充截图或人工视觉验收记录。

## 2. 主题覆盖规则

- 每个新 UI 组件必须在 Light/Dark 两套主题下验收。
- 截图验收必须使用可显示中文字体的环境；UI 启动入口应优先配置 `Microsoft YaHei UI`、`Microsoft YaHei`、`SimSun`、`Noto Sans CJK SC`、`Source Han Sans SC` 等中文字体 fallback，避免截图和最终用户界面出现方框字。
- 禁止依赖 Qt 默认浅色背景。凡是 `QTableWidget`、`QTreeView`、`QListView`、`QTabWidget`、`QTabBar`、`QLineEdit`、`QComboBox`、`QScrollArea`、`QHeaderView`、`QToolButton` 或自定义 `QFrame`，都必须有明确主题样式。
- 对复合控件必须检查内部区域：例如表格要检查 viewport、header、corner、grid、selection；页签要检查 pane、tab、selected tab、hover tab；滚动区域要检查 scrollbar 和 handle。
- Dark 主题验收不得出现大块纯白或系统默认浅灰区域，除非该区域是用户数据内容且有明确设计说明。

## 3. 图标与按钮规则

- 图标规范以 [UI 图标规范](./ui-icon-guidelines.md) 为准。
- 工具栏、侧边栏、状态栏和抽屉页签的图标必须通过 `xtable.ui.icons.icon_for(icon_id, theme, state)` 获取。
- `QAction` 和关键按钮必须设置 `icon-id` 属性，便于主题切换和测试。
- 侧边栏按钮必须使用专用样式，不能继承系统默认按钮背景；尺寸、选中态、hover 态和图标对比度必须在两套主题下可读。
- 高频操作按钮默认只显示图标，文本进入 tooltip、accessibleName 和菜单项。

## 4. 诊断抽屉规则

- 问题、日志和诊断详情统一使用底部诊断抽屉承载。
- 底部诊断抽屉必须支持页签切换，基础页签为 `问题` 和 `日志`。
- 底部诊断抽屉必须可调整高度。默认高度建议 220px，最小高度不高于 160px，最大高度应允许达到窗口高度的 50%。
- 用户调整后的抽屉高度应写入 UI 配置，后续启动或打开项目时恢复。
- 状态栏问题按钮是问题面板的高频主入口；顶部工具栏不应再放置同等权重的问题入口。

## 5. 弹窗与组件治理规则

- 新 UI 需求必须先进入 `xtable.ui` 模块实现为组件、页面、Dialog 或 Shell 能力，再由 `app`、`application` 或其他业务模块调用。
- 禁止业务模块直接创建复杂 Qt 控件；业务模块只提供数据、状态、错误和回调，具体展示由 `xtable.ui` 决定。
- 统一提示弹窗使用 `xtable.ui.dialogs.MessageDialog` 或后续同级封装，业务服务只调用 `ProjectDialogs` 等 Dialog 服务，不直接创建系统默认消息框。
- 弹窗必须包含稳定 objectName：根节点、标题、正文、图标区域和按钮区都要可被测试定位。
- 弹窗按钮遵循 UI 按钮规范：确认、取消、删除、覆盖等严谨决策场景可以使用明确文本按钮；普通工具操作继续使用图标按钮。
- 每个高风险 Qt 复合控件必须先进入 UI 封装层，再给业务界面使用。当前高风险清单包括：Dialog、Table、Tab、Splitter、StatusBar、ToolBar、Menu、Input、ScrollArea。
- 复用组件的职责、objectName、状态和限制以 [UI Kit 组件说明](./ui-kit-components.md) 为准；新增组件时必须同步补充该文档。
- 设计 token 是唯一颜色来源。业务 UI 不得直接写颜色、边框、圆角、临时图标或平台默认系统图标。
- 新增或替换 UI 组件时，必须同步补充 Light/Dark 样式选择器、运行时属性测试和截图验收记录。

## 6. 验收要求

UI 改动完成后，至少提供以下证据：

- 自动化测试通过。
- 对关键控件的 objectName、icon-id、主题属性、尺寸和可见状态进行运行时检查。
- 对 Light/Dark 两套主题至少各保留一张截图或人工验收记录。
- 若问题来自评估批次，必须在 [阶段开发评估记录](./development-review.md) 中更新状态和验收结论。
- 若变更影响阶段完成度，必须同步更新 [开发日志](./development-log.md)。
