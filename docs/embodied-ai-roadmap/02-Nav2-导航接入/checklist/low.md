# Low 验收：最低可用

- `colcon build --packages-select kibot_one_sim` 通过。
- `src/kibot_one_sim/scripts/check_nav2_runtime_deps.sh` 通过；如果失败，必须先升级 FastCDR/FastRTPS 相关包。
- 当前 runtime 文件与 `reference/final-runtime/src/kibot_one_sim/` 下的同名 `.bak` 文件去掉 `.bak` 后逐文件一致。
- 按 `evidence/usage.md` 的 runtime patch 完全一致审计执行，当前 runtime diff 与 `evidence/reference-runtime.patch` 无差异。
- `ros2 launch kibot_one_sim nav2.launch.py --show-args` 能列出 launch 参数。
- `src/kibot_one_sim/config/nav2_params.yaml` 存在，并使用 `map`、`odom`、`base_link`、`/scan`。
- `src/kibot_one_sim/launch/nav2.launch.py` 不启动旧的 `mode_control`、`follow_controller`、`cmd_vel_watchdog`。
- `package.xml` 声明 `nav2_bringup` 运行依赖。
