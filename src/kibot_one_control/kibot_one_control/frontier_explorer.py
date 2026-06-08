from __future__ import annotations

from typing import Any, List, Tuple, cast

import rclpy
from action_msgs.msg import GoalStatus  # type: ignore
from nav2_msgs.action import NavigateToPose  # type: ignore
from nav_msgs.msg import OccupancyGrid  # type: ignore
from rclpy.action import ActionClient  # type: ignore
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node, Parameter
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
import rclpy.time
from tf2_ros import Buffer, TransformException, TransformListener  # type: ignore
from rclpy.task import Future

from kibot_one_control.frontier_core import GridInfo
from kibot_one_control.frontier_core import filter_cooldown_candidates
from kibot_one_control.frontier_core import find_frontier_candidates

class FrontierExplorer(Node):
    def __init__(self, node_name: str = "frontier_explorer", *, context: rclpy.Context | None = None, cli_args: List[str] | None = None, namespace: str | None = None, use_global_arguments: bool = True, enable_rosout: bool = True, start_parameter_services: bool = True, parameter_overrides: List[Parameter] | None = None, allow_undeclared_parameters: bool = False, automatically_declare_parameters_from_overrides: bool = False, enable_logger_service: bool = False) -> None:
        super().__init__(node_name="frontier_explorer", context=context, cli_args=cli_args, namespace=namespace, use_global_arguments=use_global_arguments, enable_rosout=enable_rosout, start_parameter_services=start_parameter_services, parameter_overrides=parameter_overrides, allow_undeclared_parameters=allow_undeclared_parameters, automatically_declare_parameters_from_overrides=automatically_declare_parameters_from_overrides, enable_logger_service=enable_logger_service)

        params = [
            ("map_topic", "/map"),
            ("map_frame", "map"),
            ("base_frame", "base_link"),
            ("navigate_action", "/navigate_to_pose"),
            ("exploration_period", 1.0),
            ("goal_timeout", 35.0),
            ("frontier_cooldown", 20.0),
            ("min_frontier_size", 3),
            ("min_goal_distance", 0.35),
            ("max_goal_distance", 3.0),
            ("free_threshold", 20)
        ]

        self.declare_parameters(namespace="", parameters=cast(Any, params))
        
        self.latest_map: OccupancyGrid | None = None
        self.current_goal_key: str | None = None
        self.current_goal_sent_seconds: float | None = None
        self.goal_handle: Any | None = None
        self.cooled_frontiers: dict[str, float] = {}

        self.tf_buffer: Buffer = Buffer()
        self.tf_listener: TransformListener = TransformListener(buffer=self.tf_buffer, node=self)
        self.action_client: ActionClient = ActionClient(
            node=self,
            action_type=NavigateToPose,
            action_name=cast(str, self.get_parameter(name="navigate_action").value)
        )

        map_qos: QoSProfile = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL   
        )
        self.create_subscription(
            msg_type=OccupancyGrid,
            topic=cast(str, self.get_parameter(name="map_topic").value),
            callback=self._map_callback,
            qos_profile=map_qos
        )
        self.create_timer(
            timer_period_sec=cast(float, self.get_parameter(name="exploration_period").value),
            callback=self._exploration_tick,
        )

    def _map_callback(self, msg: OccupancyGrid) -> None:
        self.latest_map = msg
    
    def _exploration_tick(self) -> None:
        if self.current_goal_key is not None:
            self._cancel_timed_out_goal()
            return

        if self.latest_map is None:
            self.get_logger().debug(message="正在选择边界前等待 /map 的消息...")
            return

        if not self.action_client.wait_for_server(timeout_sec=0.1):
            self.get_logger().debug(message="正在等待 NavigateToPose 动作提供者...")
            return

        robot_pose = self._lookup_robot_pose()
        if robot_pose is None:
            return

        candidate = self._select_candidate(robot_x=robot_pose[0], robot_y=robot_pose[1])
        if candidate is None:
            self.get_logger().info(message="没有找到可用的边界候选。")
            return

        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = cast(str, self.get_parameter(name="map_frame").value)
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = candidate.map_x
        goal.pose.pose.position.y = candidate.map_y
        goal.pose.pose.orientation.w = 1.0

        self.current_goal_key = candidate.key
        self.current_goal_sent_seconds = self._now_seconds()
        self.get_logger().info(
            message="在 (%.2f, %.2f) 发送边界 %s 中... ;size=%d, distance=%.2f, score=%.2f"
            % (candidate.map_x, candidate.map_y,candidate.key, candidate.size, candidate.distance, candidate.score)
        )
        future = self.action_client.send_goal_async(goal=goal)
        future.add_done_callback(callback=self._goal_response_callback)

    def _lookup_robot_pose(self) -> Tuple[float, float] | None:
        map_frame = cast(str, self.get_parameter(name="map_frame").value)
        base_frame = cast(str, self.get_parameter(name="base_frame").value)
        try:
            transform = self.tf_buffer.lookup_transform(target_frame=map_frame, source_frame=base_frame, time=rclpy.time.Time())
        except TransformException as exc:
            self.get_logger().debug(message=f"等待 {map_frame} -> {base_frame} 时出现错误: {exc}")
            return None
        
        return(
            transform.transform.translation.x,
            transform.transform.translation.y
        )
    
    def _now_seconds(self) -> float:
        return self.get_clock().now().nanoseconds / 1e9

    def _select_candidate(self, robot_x: float, robot_y: float):
        assert self.latest_map is not None
        grid = self.latest_map.info
        info = GridInfo(
            width=grid.width,
            height=grid.height,
            resolution=grid.resolution,
            origin_x=grid.origin.position.x,
            origin_y=grid.origin.position.y
        )
        candidates = find_frontier_candidates(
            data=self.latest_map.data,
            info=info,
            robot_x=robot_x,
            robot_y=robot_y,
            min_frontier_size=cast(int, self.get_parameter(name="min_frontier_size").value),
            min_goal_distance=cast(float, self.get_parameter(name="min_goal_distance").value),
            max_goal_distance=cast(float, self.get_parameter(name="max_goal_distance").value),
            free_threshold=cast(int, self.get_parameter(name="free_threshold").value)
        )
        available = filter_cooldown_candidates(candidates=candidates, cooled_frontiers=self.cooled_frontiers, now_seconds=self._now_seconds())

        return available[0] if available else None
    
    
    def _goal_response_callback(self, future: Future) -> None:
        goal_handle = future.result()
        if not goal_handle or not goal_handle.accepted:
            self.get_logger().warning(message=f"发送边界目标 {self.current_goal_key} 被拒绝")
            self._cool_current_frontier()
            self._clear_current_goal()
            return
        
        self.goal_handle = goal_handle
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._goal_result_callback)

    def _goal_result_callback(self, future: Future) -> None:
        result = future.result()
        if result is None:
            return
        
        status = result.status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(message=f"边界目标 {self.current_goal_key} 完成")
        else:
            self.get_logger().warning(message=f"边界目标 {self.current_goal_key} 已完成，状态： {status}")
            self._cool_current_frontier()
        self._clear_current_goal()


    def _cancel_timed_out_goal(self) -> None:
        if self.goal_handle is None or self.current_goal_sent_seconds is None:
            return
        
        timeout = cast(float, self.get_parameter(name="goal_timeout").value)
        if self._now_seconds() - self.current_goal_sent_seconds <= timeout:
            return
        
        self.get_logger().warning(message=f"边界目标 {self.current_goal_key} 超时，取消中...")
        self.goal_handle.cancel_goal_async()
        self._cool_current_frontier()
        self._clear_current_goal()

    
    def _cool_current_frontier(self) -> None:
        if self.current_goal_key is None:
            return
        cooldown = cast(float, self.get_parameter(name="frontier_cooldown").value)
        self.cooled_frontiers[self.current_goal_key] = self._now_seconds() + cooldown

    def _clear_current_goal(self) -> None:
        self.current_goal_key = None
        self.current_goal_sent_seconds = None
        self.goal_handle = None

def main(args=None) -> None:
    explorer = None
    try:
        rclpy.init(args=args)
        explorer = FrontierExplorer()
        rclpy.spin(node=explorer)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if explorer is not None:
            explorer.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
