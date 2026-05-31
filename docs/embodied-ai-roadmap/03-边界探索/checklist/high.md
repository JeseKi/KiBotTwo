# High 验收

集成级验收证明阶段 03 可以作为阶段 06 的可靠前置。

- 探索过程中不存在多个 `/clock` publisher 或残留 Gazebo server。
- goal rejected、failed 或 timeout 后，对应 frontier key 进入 cooldown。
- 当前 goal 成功后，explorer 会继续选择下一个 frontier。
- 视觉任务后续需要中断探索时，可以通过取消当前 `/navigate_to_pose` goal 实现，不需要改 Nav2 内部参数。
- 从共同 baseline 重做 runtime 代码后，非 `docs/` diff 与 `evidence/reference-runtime.patch` 完全一致。
