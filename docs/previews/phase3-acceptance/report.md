# Phase 3 Acceptance Test Report

**Date:** 2026-05-27 19:11:09

**Result:** FAIL

**Summary:** 91/95 passed, 4 failed

## Failed Tests

- **[P1]** QButtonGroup 未被 GC 回收: group()=None → QButtonGroup 局部变量已被 GC 回收，模式切换将失效
- **[P1]** 切换到结构模式 (stackIndex=1): currentIndex=0
- **[P1]** 数据按钮取消选中(互斥): data_checked=True
- **[P1]** 剩余表格为heroes: current=None

## Screenshots

- app-initial-state: `C:\XTable\docs\previews\phase3-acceptance\01-app-initial-state.png`
- structure-mode: `C:\XTable\docs\previews\phase3-acceptance\02-structure-mode.png`
- table-metadata-edited: `C:\XTable\docs\previews\phase3-acceptance\03-table-metadata-edited.png`
- fields-after-add: `C:\XTable\docs\previews\phase3-acceptance\04-fields-after-add.png`
- fields-after-reorder: `C:\XTable\docs\previews\phase3-acceptance\05-fields-after-reorder.png`
- inspector-field-selected: `C:\XTable\docs\previews\phase3-acceptance\06-inspector-field-selected.png`
- dark-theme: `C:\XTable\docs\previews\phase3-acceptance\07-dark-theme.png`
- light-theme: `C:\XTable\docs\previews\phase3-acceptance\08-light-theme.png`
- data-mode: `C:\XTable\docs\previews\phase3-acceptance\09-data-mode.png`
- new-table-created: `C:\XTable\docs\previews\phase3-acceptance\10-new-table-created.png`
- table-deleted: `C:\XTable\docs\previews\phase3-acceptance\11-table-deleted.png`
- stress-test-final: `C:\XTable\docs\previews\phase3-acceptance\12-stress-test-final.png`
