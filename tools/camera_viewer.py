#!/usr/bin/env python3
"""Serve a local HTML camera viewer for ROS 2 image topics."""

from __future__ import annotations

import argparse
import json
import signal
import sys
import threading
import time
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import cv2
import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from kibot_one_interface.msg import FlagDetection  # type: ignore
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image  # type: ignore


INDEX_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>KiBot Camera Viewer</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #101418;
      --panel: #171d23;
      --line: #2a343d;
      --text: #ecf2f7;
      --muted: #91a0ad;
      --ok: #42d17d;
      --warn: #ffcc66;
      --bad: #ff6b6b;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    main {
      width: min(1120px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 20px 0 28px;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 16px;
    }
    h1 {
      margin: 0;
      font-size: 20px;
      font-weight: 650;
      letter-spacing: 0;
    }
    .status {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
      color: var(--muted);
      font-size: 14px;
      white-space: nowrap;
    }
    .dot {
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: var(--warn);
      box-shadow: 0 0 12px color-mix(in srgb, var(--warn), transparent 40%);
    }
    .dot.ok {
      background: var(--ok);
      box-shadow: 0 0 12px color-mix(in srgb, var(--ok), transparent 40%);
    }
    .dot.bad {
      background: var(--bad);
      box-shadow: 0 0 12px color-mix(in srgb, var(--bad), transparent 40%);
    }
    .viewer {
      background: #07090b;
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      aspect-ratio: 4 / 3;
      display: grid;
      place-items: center;
    }
    .viewer img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      image-rendering: auto;
    }
    .metrics {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-top: 12px;
    }
    .metric {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 12px;
    }
    .label {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.2;
      margin-bottom: 6px;
    }
    .value {
      font-size: 18px;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }
    @media (max-width: 720px) {
      main { width: min(100vw - 20px, 1120px); padding-top: 12px; }
      header { align-items: flex-start; flex-direction: column; gap: 8px; }
      .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .value { font-size: 16px; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>KiBot Camera Viewer</h1>
      <div class="status"><span id="dot" class="dot"></span><span id="state">waiting for frames</span></div>
    </header>
    <section class="viewer" aria-label="camera stream">
      <img src="/stream.mjpg" alt="camera stream">
    </section>
    <section class="metrics">
      <div class="metric"><div class="label">Detection</div><div id="detected" class="value">-</div></div>
      <div class="metric"><div class="label">Confidence</div><div id="confidence" class="value">-</div></div>
      <div class="metric"><div class="label">Center</div><div id="center" class="value">-</div></div>
      <div class="metric"><div class="label">Pixels</div><div id="pixels" class="value">-</div></div>
    </section>
  </main>
  <script>
    const state = document.getElementById("state");
    const dot = document.getElementById("dot");
    const detected = document.getElementById("detected");
    const confidence = document.getElementById("confidence");
    const center = document.getElementById("center");
    const pixels = document.getElementById("pixels");

    function fmtNumber(value, digits = 1) {
      return Number.isFinite(value) ? value.toFixed(digits) : "-";
    }

    async function refreshStatus() {
      try {
        const response = await fetch("/status.json", { cache: "no-store" });
        const data = await response.json();
        const age = data.frame_age_seconds;
        const hasFrame = data.frame_count > 0 && age !== null && age < 2.0;
        dot.className = hasFrame ? "dot ok" : "dot";
        state.textContent = hasFrame
          ? `${data.width}x${data.height} ${data.encoding} · ${fmtNumber(age, 2)}s ago`
          : "waiting for frames";

        if (data.detection) {
          detected.textContent = data.detection.detected ? "true" : "false";
          confidence.textContent = fmtNumber(data.detection.confidence, 3);
          center.textContent = `${fmtNumber(data.detection.center_x)}, ${fmtNumber(data.detection.center_y)}`;
          pixels.textContent = String(data.detection.pixel_count);
        } else {
          detected.textContent = "-";
          confidence.textContent = "-";
          center.textContent = "-";
          pixels.textContent = "-";
        }
      } catch (error) {
        dot.className = "dot bad";
        state.textContent = "viewer service unavailable";
      }
    }

    refreshStatus();
    setInterval(refreshStatus, 500);
  </script>
</body>
</html>
"""


@dataclass(frozen=True)
class DetectionSnapshot:
    detected: bool
    center_x: float
    center_y: float
    image_width: int
    image_height: int
    pixel_count: int
    confidence: float
    stamp_seconds: float

    def to_json(self) -> dict[str, Any]:
        return {
            "detected": self.detected,
            "center_x": self.center_x,
            "center_y": self.center_y,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "pixel_count": self.pixel_count,
            "confidence": self.confidence,
            "age_seconds": max(0.0, time.monotonic() - self.stamp_seconds),
        }


class ViewerState:
    def __init__(self, *, jpeg_quality: int, min_red: int, red_margin: int) -> None:
        self.jpeg_quality = jpeg_quality
        self.min_red = min_red
        self.red_margin = red_margin
        self.condition = threading.Condition()
        self.latest_bgr: np.ndarray | None = None
        self.latest_jpeg: bytes | None = None
        self.latest_detection: DetectionSnapshot | None = None
        self.frame_count = 0
        self.width = 0
        self.height = 0
        self.encoding = ""
        self.frame_id = ""
        self.last_frame_time: float | None = None
        self.last_error: str | None = None

    def update_frame(
        self,
        *,
        bgr: np.ndarray,
        width: int,
        height: int,
        encoding: str,
        frame_id: str,
    ) -> None:
        with self.condition:
            self.latest_bgr = bgr
            self.width = width
            self.height = height
            self.encoding = encoding
            self.frame_id = frame_id
            self.frame_count += 1
            self.last_frame_time = time.monotonic()
            self.last_error = None
            self._render_locked()
            self.condition.notify_all()

    def update_detection(self, detection: DetectionSnapshot) -> None:
        with self.condition:
            self.latest_detection = detection
            if self.latest_bgr is not None:
                self._render_locked()
                self.condition.notify_all()

    def set_error(self, message: str) -> None:
        with self.condition:
            self.last_error = message

    def get_jpeg(self, timeout: float = 1.0) -> bytes | None:
        with self.condition:
            if self.latest_jpeg is None:
                self.condition.wait(timeout=timeout)
            return self.latest_jpeg

    def status(self) -> dict[str, Any]:
        with self.condition:
            frame_age = (
                None
                if self.last_frame_time is None
                else max(0.0, time.monotonic() - self.last_frame_time)
            )
            return {
                "frame_count": self.frame_count,
                "width": self.width,
                "height": self.height,
                "encoding": self.encoding,
                "frame_id": self.frame_id,
                "frame_age_seconds": frame_age,
                "last_error": self.last_error,
                "detection": (
                    None if self.latest_detection is None else self.latest_detection.to_json()
                ),
            }

    def _render_locked(self) -> None:
        if self.latest_bgr is None:
            return

        frame = self.latest_bgr.copy()
        detection = self.latest_detection
        if detection is not None:
            self._draw_detection(frame, detection)
        else:
            self._draw_text_panel(frame, ["Waiting for /flag_dectection"])

        ok, encoded = cv2.imencode(
            ".jpg",
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality],
        )
        if ok:
            self.latest_jpeg = encoded.tobytes()

    def _draw_detection(self, frame: np.ndarray, detection: DetectionSnapshot) -> None:
        height, width = frame.shape[:2]
        color = (50, 220, 80) if detection.detected else (80, 180, 255)
        lines = [
            f"detected: {str(detection.detected).lower()}",
            f"confidence: {detection.confidence:.3f}",
            f"pixels: {detection.pixel_count}",
        ]
        self._draw_text_panel(frame, lines, color=color)

        if not detection.detected:
            return

        scale_x = width / max(1, detection.image_width)
        scale_y = height / max(1, detection.image_height)
        center_x = int(round(detection.center_x * scale_x))
        center_y = int(round(detection.center_y * scale_y))
        center_x = max(0, min(width - 1, center_x))
        center_y = max(0, min(height - 1, center_y))

        cv2.drawMarker(
            frame,
            (center_x, center_y),
            color,
            markerType=cv2.MARKER_CROSS,
            markerSize=28,
            thickness=2,
        )
        cv2.circle(frame, (center_x, center_y), 7, color, 2)

        bbox = self._red_bbox(frame)
        if bbox is not None:
            x, y, w, h = bbox
            cv2.rectangle(frame, (x, y), (x + w - 1, y + h - 1), color, 2)

    def _draw_text_panel(
        self,
        frame: np.ndarray,
        lines: list[str],
        *,
        color: tuple[int, int, int] = (230, 230, 230),
    ) -> None:
        if not lines:
            return

        x = 10
        y = 12
        line_height = 22
        panel_width = min(frame.shape[1] - 20, 260)
        panel_height = 14 + line_height * len(lines)
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (x - 4, y - 4),
            (x - 4 + panel_width, y - 4 + panel_height),
            (12, 18, 24),
            -1,
        )
        cv2.addWeighted(overlay, 0.72, frame, 0.28, 0, frame)
        for index, line in enumerate(lines):
            cv2.putText(
                frame,
                line,
                (x, y + 16 + index * line_height),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                color,
                1,
                cv2.LINE_AA,
            )

    def _red_bbox(self, frame: np.ndarray) -> tuple[int, int, int, int] | None:
        blue = frame[:, :, 0].astype(np.int16)
        green = frame[:, :, 1].astype(np.int16)
        red = frame[:, :, 2].astype(np.int16)
        mask = (red >= self.min_red) & ((red - np.maximum(green, blue)) >= self.red_margin)
        ys, xs = np.where(mask)
        if xs.size == 0:
            return None
        return (
            int(xs.min()),
            int(ys.min()),
            int(xs.max() - xs.min() + 1),
            int(ys.max() - ys.min() + 1),
        )


def image_to_bgr(msg: Image) -> np.ndarray:
    encoding = msg.encoding.lower()
    channels_by_encoding = {
        "rgb8": 3,
        "bgr8": 3,
        "rgba8": 4,
        "bgra8": 4,
        "mono8": 1,
    }
    channels = channels_by_encoding.get(encoding)
    if channels is None:
        raise ValueError(f"unsupported image encoding: {msg.encoding}")

    row_size = msg.width * channels
    if msg.step < row_size:
        raise ValueError(
            f"invalid image step {msg.step} for {msg.width}x{msg.height} {msg.encoding}"
        )

    data = np.frombuffer(bytes(msg.data), dtype=np.uint8)
    expected_size = msg.step * msg.height
    if data.size < expected_size:
        raise ValueError(f"image data is shorter than expected: {data.size} < {expected_size}")

    rows = data[:expected_size].reshape((msg.height, msg.step))
    packed = rows[:, :row_size]

    if channels == 1:
        mono = packed.reshape((msg.height, msg.width))
        return cv2.cvtColor(mono, cv2.COLOR_GRAY2BGR)

    image = packed.reshape((msg.height, msg.width, channels))
    if encoding == "rgb8":
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if encoding == "rgba8":
        return cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    if encoding == "bgra8":
        return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    return image.copy()


class CameraViewerNode(Node):
    def __init__(
        self,
        *,
        state: ViewerState,
        image_topic: str,
        detection_topic: str,
    ) -> None:
        super().__init__("camera_viewer")
        self._state = state
        self._image_sub = self.create_subscription(
            Image,
            image_topic,
            self._image_callback,
            qos_profile_sensor_data,
        )
        self._detection_sub = self.create_subscription(
            FlagDetection,
            detection_topic,
            self._detection_callback,
            10,
        )
        self.get_logger().info(f"Serving camera topic {image_topic}")
        self.get_logger().info(f"Overlaying detection topic {detection_topic}")

    def _image_callback(self, msg: Image) -> None:
        try:
            bgr = image_to_bgr(msg)
        except ValueError as exc:
            self._state.set_error(str(exc))
            self.get_logger().warning(str(exc))
            return

        self._state.update_frame(
            bgr=bgr,
            width=msg.width,
            height=msg.height,
            encoding=msg.encoding,
            frame_id=msg.header.frame_id,
        )

    def _detection_callback(self, msg: FlagDetection) -> None:
        self._state.update_detection(
            DetectionSnapshot(
                detected=bool(msg.detected),
                center_x=float(msg.center_x),
                center_y=float(msg.center_y),
                image_width=int(msg.image_width),
                image_height=int(msg.image_height),
                pixel_count=int(msg.pixel_count),
                confidence=float(msg.confidence),
                stamp_seconds=time.monotonic(),
            )
        )


def make_handler(state: ViewerState) -> type[BaseHTTPRequestHandler]:
    class CameraViewerHandler(BaseHTTPRequestHandler):
        server_version = "KiBotCameraViewer/0.1"

        def do_GET(self) -> None:
            if self.path in ("/", "/index.html"):
                self._send_bytes(
                    INDEX_HTML.encode("utf-8"),
                    content_type="text/html; charset=utf-8",
                )
                return

            if self.path == "/status.json":
                payload = json.dumps(state.status()).encode("utf-8")
                self._send_bytes(payload, content_type="application/json")
                return

            if self.path == "/stream.mjpg":
                self._send_stream()
                return

            self.send_error(HTTPStatus.NOT_FOUND)

        def do_HEAD(self) -> None:
            if self.path in ("/", "/index.html"):
                self._send_headers(
                    len(INDEX_HTML.encode("utf-8")),
                    content_type="text/html; charset=utf-8",
                )
                return

            if self.path == "/status.json":
                payload = json.dumps(state.status()).encode("utf-8")
                self._send_headers(len(payload), content_type="application/json")
                return

            self.send_error(HTTPStatus.NOT_FOUND)

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _send_bytes(self, payload: bytes, *, content_type: str) -> None:
            self._send_headers(len(payload), content_type=content_type)
            self.wfile.write(payload)

        def _send_headers(self, content_length: int, *, content_type: str) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(content_length))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()

        def _send_stream(self) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Age", "0")
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
            self.end_headers()

            last_payload: bytes | None = None
            while True:
                payload = state.get_jpeg(timeout=1.0)
                if payload is None or payload is last_payload:
                    continue
                last_payload = payload
                try:
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n")
                    self.wfile.write(f"Content-Length: {len(payload)}\r\n\r\n".encode("ascii"))
                    self.wfile.write(payload)
                    self.wfile.write(b"\r\n")
                except (BrokenPipeError, ConnectionResetError):
                    break

    return CameraViewerHandler


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve /camera/image_raw as a local HTML MJPEG viewer.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="HTTP bind host.")
    parser.add_argument("--port", type=int, default=8080, help="HTTP bind port.")
    parser.add_argument("--image-topic", default="/camera/image_raw", help="ROS image topic.")
    parser.add_argument(
        "--detection-topic",
        default="/flag_dectection",
        help="ROS flag detection topic.",
    )
    parser.add_argument(
        "--jpeg-quality",
        type=int,
        default=85,
        choices=range(1, 101),
        metavar="[1-100]",
        help="JPEG quality for the MJPEG stream.",
    )
    parser.add_argument("--min-red", type=int, default=120, help="Red threshold for debug bbox.")
    parser.add_argument(
        "--red-margin",
        type=int,
        default=45,
        help="Required red channel margin for debug bbox.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    state = ViewerState(
        jpeg_quality=args.jpeg_quality,
        min_red=args.min_red,
        red_margin=args.red_margin,
    )

    rclpy.init(args=None)
    node = CameraViewerNode(
        state=state,
        image_topic=args.image_topic,
        detection_topic=args.detection_topic,
    )
    def spin_node() -> None:
        try:
            rclpy.spin(node)
        except ExternalShutdownException:
            pass

    spin_thread = threading.Thread(target=spin_node, daemon=True)
    spin_thread.start()

    server = ThreadingHTTPServer((args.host, args.port), make_handler(state))

    def stop(_signum: int, _frame: Any) -> None:
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    print(f"Open http://{args.host}:{args.port}/")
    try:
        server.serve_forever()
    finally:
        node.destroy_node()
        rclpy.shutdown()
        spin_thread.join(timeout=2.0)
        server.server_close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
