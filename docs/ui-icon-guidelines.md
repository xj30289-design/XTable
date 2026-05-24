# XTable UI 图标规范

## 1. 适用范围

本规范适用于工具栏、侧边栏、状态栏、诊断抽屉页签、菜单项和其他通用操作入口。

## 2. 图标风格

- 风格：扁平、几何化、单线或低填充。
- 线宽：默认 1.8px。
- 圆角：保持统一的 round cap 与 round join。
- 尺寸：
  - 工具栏：18-20px 显示尺寸。
  - 侧边栏：22-24px 显示尺寸。
  - 状态栏：14-16px 显示尺寸。
- 图标按钮不显示动作文字，动作含义通过 `tooltip`、`accessibleName` 和菜单文本表达。

## 3. 主题颜色

图标颜色必须由主题 token 控制，不得在业务 UI 中写死黑色或彩色。

- normal：普通操作。
- accent：选中或高亮。
- warn：警告。
- error：错误。
- success：成功或正常。
- info：信息。

Light 与 Dark 主题需要分别提供可读颜色，保证图标、菜单、工具栏、状态栏和抽屉内容在两套主题下都可识别。

## 4. 图标 ID

当前基础图标 ID：

- `project-new`
- `project-open`
- `project-save`
- `import`
- `export`
- `validate`
- `undo`
- `redo`
- `theme`
- `issues`
- `logs`
- `diagnostics`
- `table`
- `enum`
- `meta`
- `ok`
- `warn`
- `error`
- `info`

新增图标必须先注册稳定 icon id，再接入 action、导航或状态组件。

## 5. 实现约定

- 图标统一由 `xtable.ui.icons.icon_for(icon_id, theme, state)` 获取。
- `QAction` 和关键按钮必须设置 `icon-id` 属性，便于测试和主题切换。
- SVG 资源集中放置在 `src/xtable/ui/resources/icons/`，每个 icon id 对应一个同名 `.svg` 文件。
- SVG 文件使用 `{color}` 占位符，由 `icon_for(icon_id, theme, state)` 根据主题和状态替换为实际颜色。
- 禁止在业务 UI 中直接读取 SVG 文件或手写图标路径，必须通过统一 icon loader 获取图标。
