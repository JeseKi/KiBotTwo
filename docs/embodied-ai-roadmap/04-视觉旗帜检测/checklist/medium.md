# Medium 验收

功能完整验收用于证明“检测节点的主要输入输出规则可用”。

- 红色旗面进入相机视野时，`/flag_detection.detected` 至少在一帧中为 `true`。
- `header.frame_id` 预期为 `camera_link`。
- `center_x` 和 `center_y` 落在图像尺寸范围内。
- `pixel_count` 大于等于 `min_pixel_count`。
- 使用非红色或红色像素不足的测试图像时，纯算法返回 `detected=false`。
- `flag_detector` 不订阅 `/flag_pose`。
