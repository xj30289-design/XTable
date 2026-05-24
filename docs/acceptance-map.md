# XTable Phase 0/1 验收映射清单

本文档把开发计划中的 Phase 0/1 验收标准映射到自动化测试或人工验收项。自动化测试通过只代表对应行为已被程序检查，不等同于人工验收完成。

## Phase 0：工程骨架与技术基线

| 验收标准 | 自动化测试 | 人工验收项 | 当前状态 |
| --- | --- | --- | --- |
| 应用可启动 | `tests/test_main_window.py`、`tests/test_editor_entrypoint.py` | 双击 `open_editor.bat`，确认主窗口正常打开 | 待人工验收 |
| 主窗口包含顶部工具栏、中间工作区、左侧功能栏、底部状态栏 | `test_main_window_exposes_phase_one_project_actions` | 检查工具栏、工作区、侧栏、状态栏边界清晰 | 待人工验收 |
| 基础主题可用 | `test_dark_theme_stylesheet_covers_toolbar_menu_tooltip_and_states` | 切换 Dark/Light，检查工具栏、菜单、状态栏、提示文字可读 | 待人工验收 |
| 测试命令可执行 | `python -m pytest` | 查看测试输出无失败 | 待人工验收 |

## Phase 1：项目与文件系统

| 验收标准 | 自动化测试 | 人工验收项 | 当前状态 |
| --- | --- | --- | --- |
| 用户能创建本地项目 | `test_create_project_writes_reopenable_config_and_directories` | 从 UI 新建项目，确认目录和配置文件生成 | 待人工验收 |
| 用户能重新打开本地项目 | `test_create_project_writes_reopenable_config_and_directories` | 关闭后重新打开同一项目目录 | 待人工验收 |
| 项目设置可保存 | `test_create_project_config_contains_schema_paths_export_and_metadata`、`test_open_legacy_project_migrates_missing_schema_defaults` | 修改后保存，确认配置结构完整 | 待人工验收 |
| 外部修改不会被静默覆盖 | `test_save_project_preserves_external_changes_by_rejecting_stale_snapshot` | 手工修改配置文件后尝试保存，应提示冲突 | 待人工验收 |
| 只读、占用或写入失败有明确处理 | `test_save_project_rejects_read_only_config`、`test_save_project_classifies_common_io_failures` | 设置只读或占用文件后保存，检查提示类型 | 待人工验收 |
| 写入中断不破坏项目配置 | `test_save_project_keeps_original_config_when_atomic_replace_fails` | 模拟替换失败后确认原配置仍可打开 | 待人工验收 |
| 最近项目记录可用 | `test_recent_projects_are_updated_without_duplicates`、`test_recent_projects_ignores_damaged_store` | 打开多个项目，确认最近项目记录去重 | 待人工验收 |
| UI 侧栏和问题入口可用 | `test_main_window_switches_core_panels_and_exposes_semantic_rail_buttons`、`test_main_window_toggles_theme_and_issue_drawer` | 点击 Table/Enum/Meta 和问题入口，检查切换与底部抽屉 | 待人工验收 |
