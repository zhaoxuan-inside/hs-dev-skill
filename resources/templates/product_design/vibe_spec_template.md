# ==============================================================================
# VIBECODING EXECUTION SPEC (Machine-Actionable Contract)
# Target Feature: {feature_name}
# Source PRD: _02_product_design/{feature_name}_prd.md
# Source Prototype: _03_product_figma/{feature_name}_prototype.md
# 读写约定：专供 VibeCoding / AI 编码工具快速消费；高信息密度、零叙事废话、可直接映射代码与测试。
# ==============================================================================

meta:
  feature_id: "{FEAT-XXX}"
  feature_name: "{feature_name}"
  density: "compact | balanced | airy"
  max_container_width: "1440px"
  primary_anchor_cta: "{具象主按钮，如：+ 创建采购订单}"

# 1. 结构化 Design Tokens 代码映射（可直接拷入 CSS Variables / Tailwind 配置）
design_tokens:
  css_variables:
    --color-primary: "#1A1C1E"
    --color-secondary: "#6C7278"
    --color-accent: "#B8422E"       # CTA 专用高亮色，首屏严格预算 ≤3 处
    --color-canvas: "#F7F5F2"
    --color-surface: "#FFFFFF"
    --color-semantic-success: "#1B873F"
    --color-semantic-warning: "#C47D00"
    --color-semantic-error: "#D9383A"
    --radius-sm: "4px"
    --radius-md: "8px"
    --radius-lg: "12px"
  tailwind_shorthands:
    primary_btn: "bg-[#B8422E] text-white hover:brightness-105 active:scale-95 h-9 px-4 rounded-md font-medium text-sm transition-all inline-flex items-center justify-center select-none"
    secondary_btn: "bg-white text-[#1A1C1E] border border-gray-300 hover:bg-gray-50 active:scale-95 h-9 px-3 rounded-md font-medium text-sm transition-all"
    surface_card: "bg-white border border-gray-200 shadow-sm rounded-lg p-5"
    table_header: "bg-[#F7F5F2] text-[#6C7278] text-xs font-semibold uppercase tracking-wider px-4 py-3 text-left"

# 2. 组件树 DOM 骨架与层次结构（映射代码组件结构与插槽）
component_tree:
  - component: "{Feature}WorkbenchShell"
    layout: "flex h-screen bg-[#F7F5F2] overflow-hidden"
    slots:
      - slot: "sidebar"
        component: "NavigationSidebar"
        props: { width: "220px", activeKey: "{key}", maxItems: 5 }
      - slot: "workspace"
        layout: "flex-1 flex flex-col p-6 overflow-hidden"
        children:
          - component: "ActionBar"
            elements:
              - type: "SearchInput"
                props: { shortcut: "cmd+k", placeholder: "搜索名称/编号...", debounceMs: 300 }
              - type: "FilterTabs"
                options: ["全部(24)", "进行中(6)", "已完成(18)"]
              - type: "ProgressiveDisclosureToggle"
                props: { label: "高级筛选 ▾", target: "AdvancedFiltersDrawer" }
              - type: "PrimaryCTA"
                props: { label: "{+ 具象操作}", action: "open_create_drawer", accent: true }
          - component: "MainDataTable"
            props: { rowKey: "id", pagination: true, pageSize: 20 }
            columns:
              - { key: "id", title: "编号", width: "160px", mono: true }
              - { key: "name", title: "核心名称", width: "220px" }
              - { key: "metric", title: "核心指标", width: "140px", align: "right", mono: true }
              - { key: "status", title: "状态", width: "100px", component: "StatusBadge" }
              - { key: "actions", title: "操作", width: "120px" }
            states:
              empty: { illustration: "empty_box", title: "暂无数据", cta: "创建首条记录", action: "open_create_drawer" }
              loading: { type: "skeleton", rows: 5, pulse: true }
              error: { retryAction: "refetch_data", preserveFilters: true }

# 3. 核心交互状态机矩阵 (State Machine & Guardrails)
state_machine:
  drawer_editor:
    initial: "CLOSED"
    states:
      CLOSED:
        on: { OPEN: "OPEN_CLEAN" }
      OPEN_CLEAN:
        on: { INPUT_CHANGE: "OPEN_DIRTY", CLOSE_CLICK: "CLOSED", ESC_KEY: "CLOSED" }
      OPEN_DIRTY:
        on:
          INPUT_CHANGE: "OPEN_DIRTY"
          CLOSE_CLICK: "CONFIRM_DISCARD_MODAL"
          ESC_KEY: "CONFIRM_DISCARD_MODAL"
          SUBMIT_CLICK: "SUBMITTING"
      CONFIRM_DISCARD_MODAL:
        on:
          CONFIRM_DISCARD: "CLOSED"
          CANCEL_DISCARD: "OPEN_DIRTY"
      SUBMITTING:
        entry: "disable_cta, debounce_lock(400ms), show_spinner"
        on:
          SUBMIT_SUCCESS: "CLOSED (trigger: toast_success, prepend_table_row)"
          SUBMIT_ERROR: "OPEN_DIRTY (trigger: inline_field_errors, keep_inputs)"

# 4. 字段级输入与约束字典 (Field Constraints Dictionary)
field_constraints:
  - field: "{field_name_1}"
    layer: "primary_screen"     # primary_screen 首屏必填 / progressive_fold 折叠展开
    type: "string"
    required: true
    min_length: 2
    max_length: 50
    regex: "^[a-zA-Z0-9_\\-\\u4e00-\\u9fa5]+$"
    default: ""
    placeholder: "请输入具体的{名称}..."
    error_message: "名称长度需在 2-50 字以内，不支持特殊符号"

  - field: "{field_name_2}"
    layer: "progressive_fold"
    type: "number"
    required: false
    min: 1
    max: 999999
    default: 1
    error_message: "数值必须为大于 0 的有效整数"

# 5. 可直接生成自动化测试的 Gherkin 断言 (Executable Gherkin Test Specs)
executable_tests_gherkin:
  - id: "TEST-01-HAPPY-PATH"
    scenario: "主流程正常创建闭环"
    given: "用户打开新建抽屉且已按规则填妥所有必填项"
    when: "点击提交按钮"
    then: "按钮立即呈现 Loading 防抖态；抽屉关闭；列表第一行新增该记录；弹出 Toast 成功通知"

  - id: "TEST-02-DIRTY-FORM-GUARD"
    scenario: "未保存脏数据退出拦截保护"
    given: "用户在抽屉中输入了内容，表单处于 dirty 状态"
    when: "用户点击背景遮罩层或按下 Esc"
    then: "拦截退出，弹出二次确认弹窗提示『有未保存的更改，是否放弃？』"

  - id: "TEST-03-VALIDATION-INLINE"
    scenario: "必填项缺失原位校验与草稿保护"
    given: "用户未填写必填字段"
    when: "触发提交动作"
    then: "首个错误项红框聚焦，原位展示具体修复建议，表单阻止发送且其余已填内容 100% 保留"

  - id: "TEST-04-EMPTY-FTUE"
    scenario: "首次零数据进入呈现冷启动引导"
    given: "新用户首次进入且数据为空"
    when: "页面加载完成"
    then: "主区域展示空状态插画、引导说明及『创建首条记录』主 CTA，无死胡同"

# 6. 机器硬护栏与反模式禁止清单 (Hard DO NOTs for AI / VibeCoding)
hard_guardrails:
  - "STRICTLY FORBIDDEN: 在首屏平铺超过 5 个并列筛选控件（次要项必须放入高级筛选折叠面板或抽屉）"
  - "STRICTLY FORBIDDEN: 按钮文案写笼统的『确定/提交/OK』（必须写『创建采购订单』等具象动词+宾语）"
  - "STRICTLY FORBIDDEN: 提交失败或网络超时清空表单（必须保留用户已输入的内容）"
  - "STRICTLY FORBIDDEN: 在缺乏字段约束校验的情况下直接调用后端接口"
  - "STRICTLY FORBIDDEN: 首屏使用超过 3 处 Accent 强调色高亮"
