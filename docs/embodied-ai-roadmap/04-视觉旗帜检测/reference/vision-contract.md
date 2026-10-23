# 视觉检测契约

## Topic

| 名称 | 类型 | 方向 | 来源 / 消费者 |
| --- | --- | --- | --- |
| `/camera/image_raw` | `sensor_msgs/msg/Image` | Gazebo -> ROS2 | `front_camera` 经 `ros_gz_bridge` 发布，`flag_detector` 订阅 |
| `/flag_detection` | `kibot_one_interface/msg/FlagDetection` | ROS2 内部 | `flag_detector` 发布，阶段 06 任务状态机消费 |
| `/flag_pose` | `geometry_msgs/msg/PoseStamped` | Gazebo -> ROS2 | 仅保留为 debug 对照，不作为任务输入 |

### 运行时接线

- `flag_detector` 的 `image_topic` 和 `detection_topic` 默认值分别为 `/camera/image_raw` 和 `/flag_detection`。
- `flag_detection.launch.py` 暴露同名参数并传递给检测节点；已有相机或测试图像源可以使用 `start_sim:=false`。
- `tools/camera_viewer.py` 默认订阅同一组话题，可通过 `--image-topic`、`--detection-topic` 覆盖。
- 图像订阅使用 sensor-data QoS（best effort、volatile）；检测输出使用 reliable、volatile、keep last 10。检测消费者应使用兼容 QoS。
- 旧拼写 `/flag_dectection` 不再默认发布或订阅。已有外部消费者应迁移到 `/flag_detection`；如需临时接入旧节点，显式设置 `detection_topic` 或 ROS remap，并在预览工具中指定相同话题。

完整回归命令、无仿真验证和影响范围见 [接口回归验证](flag-detection-regression.md)。

## `FlagDetection.msg`

```text
std_msgs/Header header
bool detected
float32 center_x
float32 center_y
uint32 image_width
uint32 image_height
uint32 pixel_count
float32 confidence
```

字段含义：

| 字段 | 含义 |
| --- | --- |
| `header` | 直接沿用输入图像 header；`frame_id` 预期为 `camera_link` |
| `detected` | 当前帧是否检测到足够大的红色旗面区域 |
| `center_x` / `center_y` | 红色像素质心，单位是图像像素 |
| `image_width` / `image_height` | 输入图像尺寸 |
| `pixel_count` | 满足红色阈值的像素数量 |
| `confidence` | `pixel_count / (image_width * image_height)`，上限为 `1.0` |

## 状态规则

- 当前帧红色像素数量大于等于 `min_pixel_count` 时，`detected=true`。
- 当前帧红色像素数量低于阈值、图像尺寸无效、encoding 不支持或数据长度不足时，`detected=false`。
- `detected=false` 时，`center_x=0.0`、`center_y=0.0`；`pixel_count` 可以保留本帧红色噪声数量。
- 检测节点逐帧发布结果，不在阶段 04 内做多帧滞回；阶段 06 可以根据任务需要增加状态机级去抖。

## 坐标边界

阶段 04 只承诺图像平面检测：

- 输出是 `camera_link` 图像帧中的像素观测。
- 不输出 `world`、`map`、`odom` 或 `base_link` 下的旗帜坐标。
- 不读取 `/flag_pose`。
- 不把视觉检测伪装成 `/flag_pose`。

阶段 05 如果要靠近旗帜，应基于本阶段的 `center_x`、`center_y`、`image_width`、`image_height` 和后续测距策略继续估计方向或位置。

## 04B 的兼容边界

YOLO 接入时继续使用上述话题、QoS 和 `FlagDetection.msg` 字段类型，保留输入图像的时间戳、frame_id、尺寸和像素坐标单位；无目标时继续发送 `detected=false` 并清空中心坐标。定位和任务节点通过这个消息消费观测。

本页的红色像素数量和面积占比公式描述的是颜色 backend。YOLO 的 bbox center、`pixel_count` 和模型分数如何映射到现有字段，需要在 04B 明确定义；任务层不能把颜色面积占比当成已经校准的模型概率。此次修复保持现有字段及颜色检测语义。
