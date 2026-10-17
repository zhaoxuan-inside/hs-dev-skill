# Skill 版本检测与更新

**何时读**：会话首次加载主 Skill、用户询问更新/版本、检测到新版或执行整包升级时。

## 自动检测与提示

每个会话首次加载主 Skill 时，在宿主网络权限允许范围内执行一次：

```bash
python <安装根>/scripts/skill_update.py check --quiet
```

- 不写工程、安装目录或全局配置，不下载更新包，不自动安装；同一会话不反复检测和提醒。用户明确要求重新检查时可以再次执行。
- 有新版时向用户提示当前版本、最新版本和更新入口，并继续原任务。用户明确要求更新后才执行安装；检测不是升级授权。
- 默认查询官方仓库 `zhaoxuan-inside/hs-dev-skill` 的 GitHub 最新正式 Release。按四段数字比较，不按字符串比较；跳过草稿与预发布，不因本地开发版本领先而降级。
- 每次网络请求超时为 8 秒。网络受限、离线、API 限流或尚无正式 Release 时，状态为 unavailable，不宣称“已经最新”；自动安静模式不输出提示、不阻断原任务，不循环重试授权。
- 手动检查用 `check`，输出 JSON 的 installed/latest/update_available/status/message/release_url/update_method/update_command；源码工作副本提示 Git 更新，普通安装提示整包更新，符号链接解析到真实安装位置。unavailable 时 update_available 为 null。自动模式只有确实存在新版才输出提示与命令 argv 数组，按参数执行，不能拼成未经转义的 shell 字符串。

## 更新入口

在线更新当前安装包（安装路径与源码仓库分开）：

```bash
python <安装根>/scripts/skill_update.py install
# 或显式选择另一个安装位置
python scripts/skill_update.py install --target /path/to/installed/hs-dev-skill
```

使用本地已验证的完整包更新，适用于本地开发版、离线分发或尚未发布的版本：

```bash
python scripts/skill_update.py install --source /path/to/source/hs-dev-skill --target /path/to/installed/hs-dev-skill
```

同版本损坏修复需显式添加 `--reinstall`。在线版本比本地旧时仍不降级。Git 源码工作副本使用 `git pull --ff-only`，先保存未提交改动；更新器拒绝覆盖包根含 `.git` 的工作副本及符号链接安装路径，避免改坏源码或链接指向。

Linux/macOS 通常使用 python3；Windows 可使用 py -3。CLI 返回 JSON；check 的失败不阻断主任务，退出码仍为 0；install 失败退出码为 1。

## 完整性、替换与恢复

1. 在线路径只接受官方 Release 中精确命名的 `hs-dev-skill-vVERSION.zip` 与 `SHA256SUMS` 附件，校验 ZIP 的 SHA-256 与包内版本。缺附件/摘要不符即停止，不能静默切到分支源码安装。
2. ZIP 限制下载与展开体积，拒绝目录穿越、绝对/Windows 驱动路径、符号链接和大小写重复成员；不执行下载包中的脚本。
3. 检查 Skill 名称、元数据/正文/README 版本、路由清单、全部子 Skill 与详规；在目标同级目录暂存完整包，排除缓存与工程运行数据。
4. 原安装先移动到暂存备份，替换后再次校验；失败立即恢复原安装，成功后清理临时备份。更新不会自动刷新用户工程的需求基线或签收。
5. 当前任务继续沿用已加载的明确基线；新版本从下次加载生效。规则语义有变化时，按原需求变更/失效协议处理，不能自动迁移签收。

SHA-256 校验用于下载完整性，不等于独立签名认证。更新器只覆盖 Skill 安装包；不要将业务工程、个人笔记或凭证存放在包内。首次使用安装完整包；既有 skills CLI 用户也可使用其安装入口重新安装，不能只更新 SKILL.md。
