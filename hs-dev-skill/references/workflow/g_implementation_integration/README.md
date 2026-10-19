# G 实现、测试与增量集成

## 目的与边界

实现当前有效任务并取得行为、集成及一致发布证据。G1 落实切片修改，G2 验证相关行为和工程检查，G3 核验实际协作及回归，G4 发布受管一致修订；按实际依赖迭代，不推迟到最后首次集成，也不要求局部任务全量重跑。

写入须满足主入口执行协议，保护已有修改并沿用有效兼容与业务契约；真实资源、替身、计划和实际结果分别记录。受管发布不等于 Git commit、push 或部署，阶段通过限定于实际覆盖范围及当前确认责任，不自动发布应用，无需额外生成阶段文档。

活动按输入依赖和影响范围连接，不按编号强制重做。

- [G1 切片实现](g1_slice_implementation/README.md)
- [G2 切片验证](g2_slice_verification/README.md)
- [G3 增量集成](g3_incremental_integration/README.md)
- [G4 一致性提交](g4_consistent_commit/README.md)
