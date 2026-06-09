# 视觉检测契约

## Topic

| 名称 | 类型 | 方向 | 来源 / 消费者 |
| --- | --- | --- | --- |
| `/camera/image_raw` | `sensor_msgs/msg/Image` | Gazebo -> ROS2 | `front_camera` 经 `ros_gz_bridge` 发布，`flag_detector` 订阅 |
| `/flag_detection` | `kibot_one_interface/msg/FlagDetection` | ROS2 内部 | `flag_detector` 发布，阶段 06 任务状态机消费 |
| `/flag_pose` | `geometry_msgs/msg/PoseStamped` | Gazebo -> ROS2 | 仅保留为 debug 对照，不作为任务输入 |

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
