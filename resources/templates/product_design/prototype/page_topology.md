## 5. 双轨页面信息架构与多端四态原型 (Dual-Track Multi-Platform Prototypes & UI Specs)

> **多端适用声明**：本项目目标前端形态为：`[ ] Web 端 (Responsive)` / `[ ] 移动端 (Mobile App/H5)` / `[ ] 桌面端 (Desktop Client)`
> 必须根据目标端型绘制对应的 Mermaid 空间拓扑与内联 UI 标注的 ASCII 比例线框图。

### 5.1 轨一：页面空间划分与流转拓扑 (Mermaid)
```mermaid
flowchart TB
  subgraph PageShell["{模块名称} 空间拓扑 (目标端: Web/桌面/移动)"]
    Header["顶栏 (H: 56px)：品牌 Logo | 全局快捷搜索 (⌘K) | 消息通知 | 工作台 [Font: 14px w500]"]
    subgraph BodyArea["核心交互工作区 (Max 1440px / 移动端 390px)"]
      Sidebar["左侧主导航 (W: 220px, 固定)：核心业务入口 (≤5 项)"]
      MainContent["中央主画布 (flex-1, 滚动)：高频工具栏 + 核心数据表 [Padding: 24px]"]
      SideInspector["右侧渐进式披露抽屉 (W: 420px, 按需滑出)：详情查看与表单编辑"]
    end
    Header --> BodyArea
    Sidebar --- MainContent --- SideInspector
  end
```

### 5.2 轨二：页面核心四态 ASCII 空间比例线框与 UI 物理参数内联标注
