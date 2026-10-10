---
version: alpha
name: <!-- 产品视觉名，非公司法定名 -->
description: <!-- 一句话：题材 + 受众 + 页面主职 -->
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
  neutral: "#F7F5F2"
  surface: "#FFFFFF"
typography:
  h1:
    fontFamily: <!-- Display / Sans -->
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: -0.02em
  body-md:
    fontFamily: <!-- Body -->
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 32px
  xl: 64px
rounded:
  sm: 4px
  md: 8px
  lg: 12px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.md}"
    padding: 12px
---

# DESIGN.md — <!-- 产品名 -->

> Agent：实现 UI 前读本文件；手艺与反 AI 皮见 Skill `frontend_craft.md`。  
> 对标来源（可选）：awesome-design-md / `<slug>` — 已改编，非品牌克隆。

## Overview

<!-- 用具体参照物写气质，禁「现代/干净/高级」空词。例：资料密集的交易终端；暖纸色编辑部；工业说明书。 -->

- **Audience**: 
- **Primary job of the UI**: 
- **Density**: <!-- airy | balanced | dense -->
- **Mood**: 

## Colors

<!-- 每色：语义名 + hex + 只用在哪里 -->

- **Primary**: 
- **Secondary**: 
- **Accent / Tertiary**: <!-- 首屏强调色预算：约 3–5 处 -->
- **Neutral / Surface**: 
- **Semantic** (success / warning / error / info): 

## Typography

- **Display / Headings**: 
- **Body**: 
- **Mono / Data** (optional): 
- **Rules**: sentence case by default; max ~2 families; large headings tracking-tight.

## Layout

- **Grid / max width**: 
- **Spacing scale**: 4/8 基阶（或项目 token）
- **Section rhythm**: 每节只做一件事；禁止统一「标题+三卡片」模板重复
- **Hero budget**: 品牌/主标题、一句支持文案、一组 CTA、一块主视觉

## Elevation & Depth

<!-- 阴影阶梯，或纯色阶/边框层级；说明何时不用阴影 -->

## Shapes

<!-- 圆角级差：输入 / 卡片 / 模态 不应同一半径 -->

## Components

### Buttons
- Primary / Secondary / Tertiary / Destructive：

### Inputs & Forms
- Label、错误、禁用：

### Cards / Surfaces
- 仅作可交互或成组容器时使用卡片

### Navigation
- 只链到真实存在的页面/锚点

## Do's and Don'ts

**Do**
- 
- 

**Don't**
- 紫靛万能渐变 / 奶油底+赤陶默认皮 / 每节 fade-up
- 假数据、假证言、未证实合规口号
- 复制对标品牌 logo、专有插画或像素级布局

## Responsive Behavior

- Breakpoints: ~320 / 768 / 1024
- Touch targets ≥ ~44px；尊重 `prefers-reduced-motion` 与 safe-area

## Agent Prompt Guide

```text
Follow project-root DESIGN.md tokens and Do's/Don'ts.
Build <page> for <audience>. One job above the fold.
No AI-default aesthetic. No fabricated stats.
```
