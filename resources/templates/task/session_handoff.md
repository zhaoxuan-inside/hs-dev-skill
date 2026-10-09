# 会话交接与断点恢复记录 (Session Handoff)

- **任务 ID**：`{task_id}`
- **中断时间**：`{timestamp}`
- **当前任务状态**：`{status}`

---

## 1. 当前执行断点 (Current Checkpoint)
{清晰描述在哪个步骤中断，正在编辑哪个文件，当前处于什么中间状态}

---

## 2. 已完成工作 (Completed Steps)
- [x] 1. ...
- [x] 2. ...

---

## 3. 遗留待办事项 (Remaining Steps)
- [ ] 1. ...
- [ ] 2. ...

---

## 4. 下一轮会话恢复 Prompt (Next Session Resume Prompt)
```text
请继续执行任务 [{task_id}]。
当前断点：{checkpoint_desc}。
请按照任务详情 _02_task_detail/_01_{task_name}/_00_task_detail.md 继续执行后续步骤。
```
