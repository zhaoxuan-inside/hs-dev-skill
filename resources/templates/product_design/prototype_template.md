# 产品设计语言与界面原型规范：{feature_name}

- **功能模块**：{feature_name}
- **创建时间**：{YYYY-MM-DD}
- **介质形式**：双轨原型（Mermaid 拓扑 + ASCII 空间比例线框） / UX 四定律 / Design Tokens 规范
- **关联 PRD**：`_02_feature_spec/_01_human_prd/{feature_name}_prd.md`
- **可交互 HTML 原型预览**：`_02_feature_spec/_03_prototype_html/{feature_name}_prototype.html`（多端视口仿真与四态直读）
- **宏观品味宪章继承**：`Inherits: /DESIGN.md`
- **状态**：DRAFT / REVIEWED / FROZEN

> [!NOTE]
> **产出铁律**：本文件专精于**模块特定功能流的 UX 可用性法则与双轨多态界面原型**。
> - **品味继承**：本项目全局调性、基准 Design Tokens、Anti-Slop 禁令均直接继承根目录 `DESIGN.md`，本文件仅定义该模块**特化/局部的组件状态与界面流**，严禁在多模块间重复定义冲突的全局规范。
> - **HTML 可视化真理源**：若产品含前端界面，必须配套产出 `{feature_name}_prototype.html`，供开发者在浏览器中免配置多端视口切换与四态走查。
> - **职责边界**：严禁在本文中写入底层技术实现细节，专注呈现局部流转、认知层级、组件六态与四态线框。


---

<!-- HS_TEMPLATE_INCLUDE: prototype/visual_components.md -->
<!-- HS_TEMPLATE_INCLUDE: prototype/page_topology.md -->
<!-- HS_TEMPLATE_INCLUDE: prototype/populated.md -->
<!-- HS_TEMPLATE_INCLUDE: prototype/empty_loading_error.md -->
<!-- HS_TEMPLATE_INCLUDE: prototype/mapping_signoff.md -->
