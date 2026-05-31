# final-runtime

这里保存阶段 03 探针分支中所有非 `docs/` runtime 变更的最终文件副本。

用途：

- 按 roadmap 手写实现后，逐文件核对最终结果。
- 文档复测时作为 `.bak` oracle。
- 配合 `../../evidence/reference-runtime.patch` 做完整 patch 一致性审计。

探针分支：

```text
roadmap-probe/03-frontier-exploration
```

探针 commit：

```text
bd5837fc9c2d90fdbc271bd6e9542110734c41cc
```

共同 baseline：

```text
6f0ef3bb59e898d3f11ecabb04518b37321be9b5
```

runtime 文件清单：

- `src/kibot_one_control/package.xml.bak`
- `src/kibot_one_control/setup.py.bak`
- `src/kibot_one_control/kibot_one_control/frontier_core.py.bak`
- `src/kibot_one_control/kibot_one_control/frontier_explorer.py.bak`
- `src/kibot_one_control/launch/frontier_exploration.launch.py.bak`
- `src/kibot_one_control/test/test_frontier_core.py.bak`
