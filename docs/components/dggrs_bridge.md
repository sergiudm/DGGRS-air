# `dggrs_bridge`

## Purpose
`dggrs_bridge` connects ROS 2 to systems that do not speak ROS directly. In this project that mainly means the operator UI on one side and the ground robot network or command endpoint on the other.

This package should stay protocol-focused. It should validate and route data, not embed perception or control logic that belongs in other packages.

## Responsibilities
- Receive click events from the operator interface over WebSocket, UDP, or another configured transport.
- Validate payload shape, coordinate bounds, and client identity before publishing ROS messages.
- Publish UI clicks onto ROS topics consumed by `dggrs_spatial_math`.
- Forward computed local goals to the ground robot over the agreed ROS topic, DDS domain, or external transport.
- Publish status, acknowledgements, and bridge health for observability.

## Recommended Interfaces
- External input payload example:

```json
{"x": 640.0, "y": 480.0, "frame_id": "camera", "timestamp_ms": 1710000000000}
```

- ROS output: `/ui/target_click` as `geometry_msgs/msg/Point`
- ROS input: `/ground_robot/goal_pose` as `geometry_msgs/msg/PoseStamped`
- Optional ROS output: `/bridge/status` as `diagnostic_msgs/msg/DiagnosticArray`

## Key Parameters
- `ui_transport`: `websocket` or `udp`
- `ui_bind_host` and `ui_bind_port`
- `ground_robot_transport`: direct ROS 2, relay node, or UDP bridge
- `allowed_origin` or client allowlist
- `click_timeout_ms`
- `goal_retry_count`

## Runtime Notes
All inbound payloads should be range-checked against the active stream resolution before publication. If the UI and video stream can drift apart in time, preserve the client timestamp and log any excessive skew. Goal forwarding should be idempotent where possible so reconnects do not duplicate commands.

## Failure Modes And Tests
Test malformed payloads, out-of-bounds clicks, disconnected UI sessions, and unreachable ground robot endpoints. Add protocol-level tests for reconnect behavior and ensure bridge logs make it obvious whether a failure occurred on ingress, ROS publication, or goal egress.
