# 阶段 02 runtime 最终文件

这个目录保存 `feat/02-Nav2-导航接入` 成品分支中的阶段 02 runtime 文件 `.bak` 完整副本。

用途：

- 作为 roadmap 增量片段的最终合并结果。
- 作为文档复测时的逐文件核对依据。
- 避免读者只按片段手写时漏掉 YAML 节点、launch 参数透传或 package 安装项。

这些文件必须与项目根目录下对应路径完全一致，只有 `docs/` 下的文件允许和成品分支不同。

对齐检查：

```bash
for path in \
  CMakeLists.txt \
  package.xml \
  config/nav2_params.yaml \
  config/ros_gz_bridge.yaml \
  launch/gazebo.launch.py \
  launch/nav2.launch.py \
  launch/sim_with_bridge.launch.py \
  scripts/check_nav2_runtime_deps.sh
do
  diff -u \
    "docs/embodied-ai-roadmap/02-Nav2-导航接入/reference/final-runtime/src/kibot_one_sim/${path}.bak" \
    "src/kibot_one_sim/${path}"
done
```

如果只想检查阶段 02 涉及的 runtime 文件，使用 `../evidence/usage.md` 中的 runtime patch 完全一致审计。
